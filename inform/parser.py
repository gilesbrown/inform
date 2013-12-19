import urllib2
import weakref
from contextlib import closing
from HTMLParser import HTMLParser
from .document import Document
from .html import Root, Element
from .html.form import Form


CHUNK_SIZE = 1024


class InformParser(HTMLParser):

    #element_classes = dict(html=Document, form=Form)
    element_classes = dict(form=Form)

    def __init__(self):
        HTMLParser.__init__(self)
        self.stack = [Root()]

    @classmethod
    def parse(cls, readable, *args, **kwargs):
        parser = cls(*args, **kwargs)
        return parser.parse_response(readable)

    def parse_response(self, readable):
        root = Root()
        self.stack = [root]
        with closing(self):
            while True:
                chunk = readable.read(CHUNK_SIZE)
                if not chunk:
                    break
                self.feed(chunk)
        return root.element

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        if tag not in self.element_classes:
            self.element_classes[tag] = Element.create_element_class(tag)
        parent = self.stack[-1] if self.stack else None
        elem = self.element_classes[tag](parent)
        self.stack.append(elem)

    def handle_endtag(self, tag):
        self.stack.pop()
