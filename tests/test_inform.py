from urlparse import urljoin
from StringIO import StringIO
from pkg_resources import resource_filename, resource_stream
from nose.tools import eq_, ok_
import inform
from .httpserver import create_server


server = create_server()
base_url = 'http://{0}:{1}/'.format(*server.server_address)
start_url = urljoin(base_url, '/start')


def setup_module():
    server.thread.start()

    
def teardown_module():
    server.shutdown()
    server.thread.join(1.0)
    assert not server.thread.is_alive()


def start(): 
    return inform.get(start_url)


def test_get_no_params():
    doc = start().elsewhere()
    eq_(doc.response.url, urljoin(base_url, '/elsewhere?x=1'))
    eq_(doc.response.status_code, 200)
    ok_('<h1>elsewhere</h1>' in doc.response.content)


def test_get_with_param():
    doc = start().get_page(page=9)
    ok_("<h1>You've reached page #9</h1>" in doc.response.content)


def test_get_with_action_query():
    doc = start().get_with_action_query()
    ok_("<h1>You've reached page #9</h1>" in doc.response.content)
    #eq_(doc.xpath('//h1/text()'), ["You've reached page #9"])


def test_get_with_hidden():
    doc = start().get_with_hidden()
    ok_("<h1>You've reached page #9</h1>" in doc.response.content)


def test_delete_page():
    doc= start().delete_page(page=9)
    eq_(doc.response.status_code, 204)


def test_upload():
    filename = resource_filename(__name__, 'upload.txt')
    doc = start().upload(content=open(filename))
    eq_(doc.response.status_code, 201)

    
def test_upload_chunked():
    stream = StringIO("How long is a a peice of this string?")
    doc = start().upload_chunked(content=stream)
    eq_(doc.response.status_code, 201)