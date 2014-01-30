""" Representation classes. """

from inform.multipart import MultipartFormData, FormData, FileValue


MISSING = object()


class Input(object):
    """ An <input> object. """

    def __init__(self, name, type=None, default=MISSING):
        self.name = name
        self.type = type
        self.default = default

    def form_data(self, value):
        if self.type == 'file' and hasattr(value, 'read'):
            value = FileValue(value)
        return [FormData(self.name, value)]
    
class Select(object):
    """ A <select> object. """
    
    def __init__(self, name, options, default=MISSING):
        self.name = name
        self.type = type
        self.options = options
        self.default = default
        
    def form_data(self, value):
        if not isinstance(value, basestring) and hasattr(value, '__iter__'):
            return [FormData(self.name, self.options[v]) for v in value]
        else:
            return [FormData(self.name, self.options[value])]


class Form(object):
    """ A <form> object. """

    def __init__(self, parser, inputs=[], action='', method='GET', enctype=None):
        self.parser = parser
        self.inputs = inputs
        self.action = action
        self.method = method
        self.enctype = enctype

    def __call__(self, **kwargs):

        form_data = []
        for form_input in self.inputs:
            value = kwargs.pop(form_input.name, form_input.default)
            if value is not MISSING:
                form_data.extend(form_input.form_data(value))

        params = None
        data = None
        headers = None

        if self.method in ('GET', 'DELETE'):
            params = form_data
        else:
            if self.enctype is not None:
                data = MultipartFormData(form_data)
                headers = data.headers(self.enctype)

        return self.parser.request(self.method, self.action,
                                   params=params, data=data, headers=headers)


class Link(unicode):
    
    def __new__(cls, parser, url):
        instance = super(Link, cls).__new__(cls, url)
        instance.parser = parser
        return instance

    def __call__(self):
        return self.parser.request('GET', self)



class Representation(object):
    def __init__(self, response):
        self.response = self.__response__ = response