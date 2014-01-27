import os
from StringIO import StringIO
from httplib import HTTPMessage
from urlparse import urlparse, parse_qs
#@UnresolvedImport

#@UnresolvedImport
from pkg_resources import resource_stream


class urllib2like_fileobj(object):
    def __init__(self, url, fileobj, code):
        self.url = url
        self.fileobj = fileobj
        self.code = code
        self.msg = HTTPMessage(StringIO())

    def info(self):
        return self.msg

    def getcode(self):
        return self.code

    def geturl(self):
        return self.url

    def __getattr__(self, attr):
        return getattr(self.fileobj, attr)


class UnableToDelete(Exception):
    pass


def url2resource(url):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    qs.pop('dummy', None)
    path_parts = ['pages', parsed.path[1:]]
    for name in ['page']:
        if name in qs:
            path_parts.append(qs[name][0])
    return os.path.join(*path_parts)


def open(method, url, headers=None, body=None):
    resource = url2resource(url)
    if method.upper() == 'DELETE':
        raise UnableToDelete(resource)
    stream = resource_stream(__name__, resource)
    return urllib2like_fileobj(url, stream, 200)
