from StringIO import StringIO
from nose.tools import eq_
from inform.chunkedtransfer import ChunkedTransferEncoding
from inform import request, form


def test_get():
    get = request.GET('http://foo.com/get')
    eq_(get.get_method(), 'GET')


def test_delete():
    delete = request.DELETE('http://foo.com/get')
    eq_(delete.get_method(), 'DELETE')


def request_with_content(method):
    url = 'http://foo.com/with_content'
    content_type = form.CONTENT_TYPE_URLENCODED
    content = 'a=b'
    request_class = getattr(request, method)
    requestobj = request_class(url, content_type, content)
    eq_(requestobj.get_method(), method)
    eq_(requestobj.get_header('Content-length'), len(content))


def test_post():
    request_with_content('POST')


def test_put():
    request_with_content('PUT')


def test_patch():
    request_with_content('PATCH')


def chunked_transfer_encoding(method):
    content_type = form.CONTENT_TYPE_URLENCODED
    url = 'http://foo.com/chunked_transfer'
    content = StringIO('123')
    request_class = getattr(request, method)
    requestobj = request_class(url, content_type, content)
    eq_(requestobj.get_method(), method)
    MISSING = object()
    assert requestobj.get_header('Content-length', MISSING) is MISSING
    eq_(requestobj.get_header('Transfer-encoding'), 'chunked')
    assert isinstance(requestobj.data, ChunkedTransferEncoding)
    # Check this gets ignored
    requestobj.add_header('Content-length', 1)
    assert requestobj.get_header('Content-length', MISSING) is MISSING
    # Check this gets ignored too
    requestobj.add_unredirected_header('Content-length', 1)
    assert requestobj.get_header('Content-length', MISSING) is MISSING
    eq_(requestobj.data.read(8192), '3\r\n123\r\n')


def test_post_with_chunked_transfer_encoding():
    chunked_transfer_encoding('POST')


def test_put_with_chunked_transfer_encoding():
    chunked_transfer_encoding('PUT')


def test_patch_with_chunked_transfer_encoding():
    chunked_transfer_encoding('PATCH')
