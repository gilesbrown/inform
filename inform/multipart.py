""" Generate multipart/form-data in pieces suitable for chunked transfer. """

import os
import mimetypes
from operator import itemgetter
from itertools import chain
from uuid import uuid4


CRLF = b'\r\n'
DASHDASH = b'--'
LEN_CRLF = len(CRLF)
LEN_HEX = len(uuid4().hex)
CONTENT_DISPOSITION = b'Content-Disposition'
CONTENT_TYPE = b'Content-Type'


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



#
# Header formatting helpers


def format_header(header_name, header_value, header_params=[]):
    return b'{0}: {1}{2}'.format(
        header_name,
        '; '.join([header_value] + list(header_params)),
        CRLF
    )


def format_header_param(param_name, param_value):
    return b'{0}="{1}"'.format(param_name, param_value)


def format_content_disposition(fieldname, filename=None):
    header_params = [format_header_param(b'name', fieldname)]
    if filename is not None:
        header_params.append(format_header_param(b'filename', filename))
    return format_header(CONTENT_DISPOSITION, b'form-data', header_params)


def format_content_type(content_type=None, boundary=None):
    if content_type is None:
        content_type = b'text/plain'
    header_params = []
    if boundary is not None:
        header_params.append(format_header_param(b'boundary', boundary))
    return format_header(CONTENT_TYPE, content_type, header_params)


def generate_boundary():
    return uuid4().hex


class Part(object):

    def __init__(self, datum):
        self.content_disposition_hdr = format_content_disposition(datum.name,
                                                              datum.filename)
        self.content_type_hdr = format_content_type(datum.content_type)
        self.datum = datum

    def __len__(self):
        return sum((
                len(self.content_disposition_hdr),
                len(self.content_type_hdr),
                LEN_CRLF,
                len(self.datum.value),
                LEN_CRLF
        ))

    def pieces(self, size):
        yield self.content_disposition_hdr
        yield self.content_type_hdr
        yield CRLF
        read = getattr(self.datum.value, 'read', None)
        if read is None:
            yield str(self.datum.value)
        else:
            while True:
                more = read(size)
                if not more:
                    break
                yield more
        yield CRLF


format_enctype_with_boundary = '{0}; boundary={1}'.format

class MultipartFormData(object):
    

    def __init__(self, data):
        self.boundary = generate_boundary()
        self.parts = [Part(datum) for datum in data
                      if datum.value is not None]
        self.pieces = None
        self.remainder = ''
        
    def headers(self, enctype):
        return {'Content-type': format_enctype_with_boundary(enctype, self.boundary)}
    
    def __nonzero__(self):
        return True

    def __len__(self):
        # We'll get a TypeError here if we have a file-like that we can't
        # get the size of.  That's ok, but it means we will fall back to
        # using "Transfer-encoding: chunked"
        len_acc = len(self.parts) * (len(DASHDASH) + len(self.boundary) +
                                      len(CRLF))
        len_acc += sum(map(len, self.parts))
        len_acc += len(DASHDASH) + len(self.boundary) + len(CRLF)
        return len_acc

    def iter_pieces(self, size_hint):
        for part in self.parts:
            yield (DASHDASH, self.boundary, CRLF)
            yield part.pieces(size_hint)
        yield (DASHDASH, self.boundary, DASHDASH, CRLF)
        
    def __iter__(self):
        while True:
            chunk = self.read()
            if not chunk:
                break
            yield chunk

    def read(self, size=None):
        if size is None:
            size = 8192
        if self.pieces is None:
            self.pieces = chain.from_iterable(self.iter_pieces(size))
        len_acc = len(self.remainder)
        pieces = [self.remainder]
        if len_acc < size:
            for piece in self.pieces:
                assert isinstance(piece, str)
                pieces.append(piece)
                len_acc += len(piece)
                if len_acc >= size:
                    break
        joined = b''.join(pieces)
        self.remainder = joined[size:]
        return joined[:size]
