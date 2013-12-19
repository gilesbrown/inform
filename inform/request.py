import urllib2
from .chunkedtransfer import ChunkedTransferEncoding


class Request(urllib2.Request):

    @classmethod
    def get_method(cls):
        return cls.__name__


def ignore_content_length(bound_add_method):
    def add_ignore_content_length(key, val):
        if key.capitalize() == 'Content-length':
            return
        bound_add_method(key, val)
    return add_ignore_content_length


class RequestWithContent(Request):

    def __init__(self, url, content_type, content):
        try:
            content_length = len(content)
            data = content
        except (TypeError, AttributeError):
            content_length = None
            # No content-length? give "Transfer-encoding: chunked" a try
            data = ChunkedTransferEncoding(content)

        Request.__init__(self, url, data)
        self.add_unredirected_header('Content-type', content_type)
        if content_length is None:
            self.add_unredirected_header('Transfer-encoding', 'chunked')
            # Trick urllib2.Request to allow "Transfer-encoding: chunked"
            # by ignoring calls to add a 'Content-length' header.
            self.add_header = ignore_content_length(self.add_header)
            self.add_unredirected_header = ignore_content_length(
                                                self.add_unredirected_header)
        else:
            self.add_unredirected_header('Content-length', content_length)


class GET(Request):
    """ HTTP GET """


class DELETE(Request):
    """ HTTP DELETE """


class POST(RequestWithContent):
    """ HTTP POST """


class PUT(RequestWithContent):
    """ HTTP PUT """


class PATCH(RequestWithContent):
    """ HTTP PATCH """
