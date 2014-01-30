import re
import json
from contextlib import closing
from collections import OrderedDict
from functools import partial
from urlparse import urljoin
from HTMLParser import HTMLParser
from .representation import Representation, Form, Link, Input, Select

class Builder(object):
    """ Base class for all builders. """
    
    builder_classes = {}
    
    def __init__(self, parser, make_url_absolute, attrs):
        self.parser = parser
        self.make_url_absolute = make_url_absolute
        self.depth = []
        self.built = []
        self.attrs = attrs
        self.text = ''
        
    def start(self, tag, attrs):
        if tag in self.builder_classes:
            cls = self.builder_classes[tag]
            return cls(self.parser, self.make_url_absolute, attrs)
        # Returning 'self' means ignore this tag
        return self
        
    def append_data(self, data):
        if len(self.depth) < 2:
            self.text += data
    
    def end(self, builder):
        self.built.append(builder.build())
        
    def build(self):
        raise NotImplementedError(self.depth)
    

class InputBuilder(Builder):
    def build(self):
        return Input(self.attrs['name'], self.attrs.get('type', None), 
                     self.attrs.get('value', None))
        
        
class OptionBuilder(Builder):
    
    def __init__(self, *args):
        Builder.__init__(self, *args)
        self.text = ''
    
    @property
    def name(self):
        return self.attrs['name']
    
    @property
    def value(self):
        return self.attrs.get('value', '').strip() or self.text
    
    @property
    def selected(self):
        return self.attrs.get('selected') == 'selected'
        
    def build(self):
        return {'name': self.attrs.get} 


class SelectBuilder(Builder):
    
    def __init__(self, *args):
        Builder.__init__(self, *args)
        self.options = OrderedDict()
        self.selected = []
   
    @property 
    def multiple(self):
        return self.attrs.get('multiple') == 'multiple'
    
    def start(self, tag, attrs):   
        if tag == 'option':
            cls = OptionBuilder
            return cls(self.parser, self.make_url_absolute, attrs)
        return self
    
    def end(self, builder):
        if builder.selected:
            self.selected.append(builder.text)
        self.options[builder.text] = builder.value
        
    def build(self):
        return Select(self.attrs['name'], self.options, self.selected)


methods_tunnelled_through_post = ['PUT', 'PATCH', 'DELETE']

class FormBuilder(Builder):
    
    builder_classes = {
        'input': InputBuilder,
        'select': SelectBuilder,
    }
    
    method_in_action = re.compile('\?_method=({0})(&|$)'.format(
        '|'.join(method.lower() for method in methods_tunnelled_through_post)
    )).search
    
    def __init__(self, *args):
        Builder.__init__(self, *args)
        self.inputs = []
    
    def start(self, tag, attrs):
        if 'name' in attrs and tag in self.builder_classes:
            cls = self.builder_classes[tag]
            return cls(self.parser, self.make_url_absolute, attrs)
        return self
    
    def build(self):
        action = self.make_url_absolute(self.attrs.get('action', ''))
        enctype = self.attrs.get('enctype', None)
        method = self.attrs.get('method', 'get').upper()
        if method == 'POST' and '?_method=' in action:
            match = self.method_in_action(action)
            if match:
                method = match.group(1).upper()
        return Form(self.parser, self.inputs, action, method, enctype)
        
    def end(self, builder):
        self.inputs.append(builder.build())


class LinkBuilder(Builder):
    def build(self):
        url = self.make_url_absolute(self.attrs.get('href', ''))
        return Link(self.parser, url)


class ValueBuilder(Builder):
    
    builder_classes = {}
    
    def build(self):
        if self.built:
            assert not self.text.strip()
            assert len(self.built) == 1
            return self.built[0]
        else:
           classes = set(self.attrs.get('class', '').split())
           if 'json' in classes:
               return json.loads(self.text)
           return self.text

class DTBuilder(ValueBuilder):
    pass

class DDBuilder(ValueBuilder):
    pass
    
class DLBuilder(Builder):
    
    builder_classes = {
        'dt': DTBuilder,
        'dd': DDBuilder,
    }
    
    def __init__(self, *args):
        Builder.__init__(self, *args)
        self.dt = None
        self.dict = OrderedDict()
        
    def end(self, builder):
        if builder.depth[0] == 'dt':
            assert not self.dt
            self.dt = builder
        else:
            assert builder.depth[0] == 'dd'
            dt = self.__dict__.pop('dt')
            dd = builder
            self.dict[dt.build()] = dd.build()
        
    def build(self):
        return self.dict

    
class LIBuilder(ValueBuilder):
    pass
        
    
class LBuilder(Builder):
    
    builder_classes = {
        'li': LIBuilder,
    }
    
    def __init__(self, *args):
        Builder.__init__(self, *args)
        self.list = []
        
    def end(self, builder):
        self.list.append(builder.build())
        
    def build(self):
        return self.list


class RepresentationBuilder(Builder):
    
    builder_classes = {
        'form': FormBuilder,
        'a': LinkBuilder,
        'dl': DLBuilder,
        'ul': LBuilder,
        'ol': LBuilder,
    }

    def __init__(self, parser, response):
        make_url_absolute = partial(urljoin, response.url)
        Builder.__init__(self, parser, make_url_absolute, {})
        self.response = response
        self.items = []

    def start(self, tag, attrs):
        if 'id' in attrs:
            cls = self.builder_classes.get(tag, ValueBuilder)
            return cls(self.parser, self.make_url_absolute, attrs)
        return self
    
    def end(self, builder):
        self.items.append((builder.attrs['id'], builder.build()))

    def build(self):
        rep = Representation(self.response)
        for (itemid, itemobj) in self.items:
            setattr(rep, itemid, itemobj)
        return rep



class InformParser(HTMLParser):
    """ Parses Inform HTML and creates 
    :class:`inform.representation.Represtation` instances.
    """

    def __init__(self, session):
        HTMLParser.__init__(self)
        self.session = session
        self.stack = []

    def request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        return self.parse(response)

    def parse(self, response):
        builder = RepresentationBuilder(self, response)
        self.stack = [builder]
        with closing(self):
            self.feed(response.content)
        return builder.build()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        builder = self.stack[-1].start(tag, attrs)
        builder.depth.append(tag)
        self.stack.append(builder)

    def handle_endtag(self, tag):
        builder = self.stack.pop()
        if builder is not self.stack[-1]:
            self.stack[-1].end(builder)
        if tag != builder.depth[-1]:
            #print self.getpos(), tag, builder.depth
            raise Exception()
        builder.depth.pop()
            
    def handle_data(self, data):
        self.stack[-1].append_data(data)
        
ValueBuilder.builder_classes.update([
    ('dl', DLBuilder),
    ('ul', LBuilder),
    ('ol', LBuilder),
    ('a', LinkBuilder),
])                                     