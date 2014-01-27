import urllib2
import weakref
from contextlib import closing
from HTMLParser import HTMLParser
from .document import Document

_link_repr = "{module}.{class}('{0.href}', {0.parser!r})".format

GET = 'GET'

class Link(unicode):
    
    def __new__(cls, href, parser):
        instance = super(Link, cls).__new__(cls, href)
        instance.parser = parser
        
    def __call__(self):
        return self.parser.request(GET, self.href)
   
    __repr__ = '{0.__class__.__name__}("{0.href}", {0.parser!r})'.format
    

class Builder(object):
    def start(self, tag, attrs):
        return self
    def end(self, child):
        pass
    
class FormBuilder(object):
    def __init__(self, tag, id):
        assert tag == 'form'
        self.id = id
        self.built = Form()
    
class NamespaceBuilder(Builder):
    builders = {
        'form' : FormBuilder,
    }
    def __init__(self, namespace):
        self.namespace = namespace
    def start(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            return self.builders[tag](tag, **attrs)
        return self
    def end(self, child):
        if child is not self:
            setattr(self.namespace, child.id, child.built)
            

class Link(object):
    def __init__(self, **kw):
        self.href = kw.pop('href')
        
class Form(object):
    
    def __init__(self):
        self.inputs = []
        
    def __call__(self, **kw):
        data = []
        for input in self.inputs:
            data.append(input.name, input.validate(kw.pop(input.name, input.value)))
        if kw:
            raise TypeError()
        
        
class AssignLink(object):
    value_class = Link


CHUNK_SIZE = 1024

class Namespace(object):
    pass

class InformParser(HTMLParser):

    #element_classes = dict(html=Document, form=Form)
    #element_classes = dict(form=Form)

    def __init__(self):
        HTMLParser.__init__(self)
        self.stack = None

    @classmethod
    def parse(cls, response, *args, **kwargs):
        parser = cls(*args, **kwargs)
        return parser.parse_response(readable)

    def parse_response(self, readable):
        root = NamespaceBuilder(Namespace())
        self.stack = [root]
        with closing(self):
            while True:
                chunk = readable.read(CHUNK_SIZE)
                if not chunk:
                    break
                self.feed(chunk)
        return root.namespace

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        self.stack.append(self.stack[-1].start(tag, attrs))

    def handle_endtag(self, tag):
        ended = self.stack.pop()
        self.stack[-1].end(ended)