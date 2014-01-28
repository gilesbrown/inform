""" Representation classes. """

from inform.multipart import MultipartFormData, FormData, FileValue


MISSING = object()


class Input(object):
    """ An <input> object. """

    def __init__(self, name, type=None, value=None):
        self.name = name
        self.type = type
        self.value = value

    def form_data(self, value):
        if self.type == 'file' and hasattr(value, 'read'):
            value = FileValue(value)
        return [FormData(self.name, value)]


class Form(object):
    """ A <form> object. """

    def __init__(self, parser, inputs, action='', method='GET', enctype=None):
        self.parser = parser
        self.inputs = inputs
        self.action = action
        self.method = method
        self.enctype = enctype

    def __call__(self, **kwargs):

        form_data = []
        for form_input in self.inputs:

            value = kwargs.pop(form_input.name, form_input.value)
            if value is MISSING:
                continue

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


class Link(object):

    def __init__(self, parser, href):
        self.parser = parser
        self.href = href

    def __call__(self):
        return self.parser.request('GET', self.href)



class Representation(object):
    def __init__(self, response):
        self.response = self.__response__ = response