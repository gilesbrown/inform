import re
from contextlib import closing
from functools import partial
from urlparse import urljoin
from HTMLParser import HTMLParser
from .representation import Representation, Form, Link, Input

class Builder(object):
    """ Base class for all builders. """
    
    def __init__(self, parser, make_url_absolute, tag, attrs):
        self.parser = parser
        self.make_url_absolute = make_url_absolute
        self.tag = tag
        self.attrs = attrs
    
    def start(self, tag, attrs):
        # Returning 'self' means ignore this tag
        return self
    
    def end(self, tag, builder):
        print "BUILDER END %r %r" % (tag, builder), builder is self
        if builder is self:
            # We don't care about the tag that has just ended
            return
        self.add(builder)
        
    def add(self, builder):
        raise NotImplementedError()
    
    def build(self):
        raise NotImplementedError(self.tag)
    

class InputBuilder(Builder):
    def build(self):
        return Input(self.attrs['name'], self.attrs.get('type', None), 
                     self.attrs.get('value', None))


class SelectBuilder(Builder):
    pass


_tunnel_methods = ['PUT', 'PATCH', 'DELETE']
_method_query_search = re.compile('\?_method=({0})(&|$)'.format('|'.join(_tunnel_methods))).search

class FormBuilder(Builder):
    
    builder_classes = {
        'input': InputBuilder,
        'select': SelectBuilder,
    }
    
    def __init__(self, *args):
        Builder.__init__(self, *args)
        self.inputs = []
    
    def start(self, tag, attrs):
        if 'name' in attrs and tag in self.builder_classes:
            cls = self.builder_classes[tag]
            return cls(self.parser, self.make_url_absolute, tag, attrs)
        return self
    
    def build(self):
        action = self.make_url_absolute(self.attrs.get('action', ''))
        enctype = self.attrs.get('enctype', None)
        method = self.attrs.get('method', 'GET')
        if method == 'POST' and '?_method=' in action:
            match = _method_query_search(action)
            if match:
                method = match.group(1)
        return Form(self.parser, self.inputs, action, method, enctype)
        
    def add(self, builder):
        self.inputs.append(builder.build())


class LinkBuilder(Builder):
    def build(self):
        url = self.make_url_absolute(self.attrs.get('href', ''))
        return Link(self.parser, url)


class ValueBuilder(Builder):
    pass

class RepresentationBuilder(Builder):
    
    builder_classes = {
        'form': FormBuilder,
        'a': LinkBuilder,
    }

    def __init__(self, parser, response):
        make_url_absolute = partial(urljoin, response.url)
        Builder.__init__(self, parser, make_url_absolute, None, {})
        self.response = response
        self.items = []

    def start(self, tag, attrs):
        if 'id' in attrs:
            cls = self.builder_classes.get(tag, ValueBuilder)
            print "HEY %r" % cls
            try:
                return cls(self.parser, self.make_url_absolute, tag, attrs)
            except Exception as exc:
                return self
        return self
    
    def add(self, builder):
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
        print "START:", self.stack, tag
        builder = self.stack[-1].start(tag, attrs)
        self.stack.append(builder)

    def handle_endtag(self, tag):
        child = self.stack.pop()
        # Tell parent in stack about 'end' of child
        self.stack[-1].end(tag, child)