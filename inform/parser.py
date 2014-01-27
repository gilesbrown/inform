from contextlib import closing
from urlparse import urljoin
from HTMLParser import HTMLParser
from .representation import Representation, Form, Link, Input


CHUNK_SIZE = 1024


class RepresentationBuilder(object):

    def __init__(self, parser, response):
        self.parser = parser
        self.response = response
        self.built = Representation(response)

    def start(self, tag, attrs):
        if tag == 'form' and 'id' in attrs:
            return FormBuilder(self.parser, self.response, tag, **attrs)
        elif tag == 'a':
            return LinkBuilder(self.parser, self.response, tag, **attrs)
        return self

    def build(self, builder):
        if builder is not self:
            setattr(self.built, builder.id, builder.built)


class InputBuilder(object):

    def __init__(self, parser, tag, **attrs):
        self.built = Input(**attrs)

    def start(self, tag, attrs):
        return self

    def build(self, builder):
        raise NotImplementedError()


class FormBuilder(object):

    def __init__(self, parser, response, tag, **attrs):
        self.response = response
        assert tag == 'form'
        self.id = attrs['id']
        action = urljoin(response.url, attrs.get('action', ''))
        method = attrs.get('method', 'GET')
        enctype = attrs.get('enctype', None)
        self.built = Form(parser, [], action, method, enctype)

    def start(self, tag, attrs):
        if tag == 'input' and 'name' in attrs:
            return InputBuilder(self.built.parser, tag, **attrs)
        return self

    def build(self, builder):
        if builder is not self:
            self.built.inputs.append(builder.built)


class LinkBuilder(object):
    def __init__(self, parser, response, tag, **attrs):
        self.id = attrs['id']
        href = urljoin(response.url, attrs.get('href', ''))
        self.built = Link(parser, href)




class InformParser(HTMLParser):

    def __init__(self, session):
        HTMLParser.__init__(self)
        self.session = session
        self.stack = None

    def request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        return self.parse(response)

    def parse(self, response):
        builder = RepresentationBuilder(self, response)
        self.stack = [builder]
        with closing(self):
            self.feed(response.content)
        return builder.built

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.stack.append(self.stack[-1].start(tag, attrs))

    def handle_endtag(self, tag):
        ended = self.stack.pop()
        self.stack[-1].build(ended)
