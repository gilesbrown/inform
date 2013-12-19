""" A client-side HTML Form class. """

import os
import mimetypes
from urllib import urlencode
from urlparse import urlsplit, urlunsplit, parse_qsl
from operator import itemgetter
from inform.multipart import MultipartFormData
from inform import request as request_module
from inform.html import Element

CONTENT_TYPE_URLENCODED = 'application/x-www-form-urlencoded'
CONTENT_TYPE_MULTIPART = 'multipart/form-data'


class Input(object):

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.type = kwargs.pop('type', None)
        self.value = kwargs.pop('value', None)
        if kwargs:
            raise ValueError('unexpected keyword argument %r' % kwargs.keys())


class Form(Element):
    """ An HTML form object following ``Inform`` conventions:
          * All <form> and <input> elements must have a 'name' attribute
          * All 'name' attributes must be valid Python identifiers.
        Each Form can be called with keyword arguments specifying input values.
    """

    def __init__(self, parent, name=None, **kwargs):
        super(Form, self).__init__(parent)
        self.method = kwargs.pop('method', 'GET')
        self.action = kwargs.pop('action', None)
        self.enctype = kwargs.pop('enctype', None)
        if kwargs:
            raise ValueError('unexpected keyword argument %r' % kwargs.keys())
        #self.form = form
#        self.parser_class = parser_class
#        self.opener = opener
        self.name = name
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            print dict(attrs)
            self.inputs.append(Input(**dict(attrs)))

    def handle_endtag(self, tag):
        #print "FORM endtag:", tag
        pass

    def __call__(self, **kw):
        """ Make an HTTP request and return a new FormResource. """
        print "CALL:", kw

        # Copy so we can use lxml to check <select> option values
        #form = deepcopy(self.form)
        form_data = []
        for form_input in self.inputs:
            value = kw.pop(form_input.name, form_input.value)
            if form_input.type == 'file' and hasattr(value, 'read'):
                value = FileValue(value)
            else:
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                elif value is None:
                    value = ''
                elif not isinstance(value, str):
                    value = str(value)
                # calling set makes lxml check <select> options
                #form_input.set('value', value.decode('utf-8'))
            form_datum = FormData(form_input.name, value)
            form_data.append(form_datum)

        # There shouldn't be any leftover arguments
        if kw:
            raise ValueError("unexpected keyword arguments %s" % kw.keys())

        # Look for "_method" input to allow PUT/DELETE/PATCH methods.
        # These can't go in form.method because that isn't standard HTML.
        input_method = form.xpath('./input[@name="_method"]/@value')
        method = input_method[0].upper() if input_method else form.method
        request_class = getattr(request_module, method)

        # Note: lxml.html takes care of making form.action an absolute link

        if method in ('GET', 'DELETE'):

            # combine action and form items into new url
            split = urlsplit(form.action)
            query_params = parse_qsl(split.query) + form_data
            url = urlunsplit(split[:-2] + (urlencode(query_params), ''))
            request = request_class(url)

        else:

            enctype = form.attrib.get('enctype', CONTENT_TYPE_URLENCODED)
            if enctype == CONTENT_TYPE_MULTIPART:
                content = MultipartFormData(form_data)
                content_type = '{0}; boundary={1}'.format(enctype,
                                                          content.boundary)
            else:
                content = urlencode(form_data)
                content_type = enctype
            request = request_class(form.action, content_type, content)

        return self.document_class(request, self.opener)


class FileValue(object):

    def __init__(self, value):
        self.value = value

    def __getattr__(self, name):
        return getattr(self.value, name)

    def __len__(self):
        try:
            return len(self.value)
        except (AttributeError, TypeError):
            pass
        return os.stat(self.value.name).st_size

    @property
    def filename(self):
        return getattr(self.value, 'name', None)

    @property
    def content_type(self):
        # Give the object a chance to define this
        content_type = getattr(self.value, 'content_type', None)
        if content_type:
            return content_type
        # Now try and guess using the file name
        filename = self.filename
        if self.filename is not None:
            content_type = mimetypes.guess_type(filename)[0]
            if content_type:
                return content_type
        # Now just fall back...
        return 'application/octet-stream'


class FormData(tuple):

    name = property(itemgetter(0))
    value = property(itemgetter(1))

    def __new__(cls, name, value):
        instance = tuple.__new__(cls, (name, value))
        return instance

    @property
    def filename(self):
        return getattr(self.value, 'filename', None)

    @property
    def content_type(self):
        return getattr(self.value, 'content_type', 'text/plain')
