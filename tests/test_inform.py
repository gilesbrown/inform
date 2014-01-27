from urlparse import urljoin
from pkg_resources import resource_filename
from nose.tools import eq_
import inform
from test.httpserver import create_server


server = create_server()
base_url = 'http://{0}:{1}/'.format(*server.server_address)
root_url = urljoin(base_url, '/root')


def setup_module():
    server.thread.start()


def teardown_module():
    server.shutdown()
    server.thread.join(1.0)
    assert not server.thread.is_alive()

#
#def test_get_no_params():
#    doc = inform.urlopen(root_url).elsewhere()
#    eq_(doc.docinfo.URL, urljoin(base_url, '/elsewhere?btn=Submit'))
#    eq_(doc.response.getcode(), 200)
#    eq_(doc.xpath('//h1/text()'), ['elsewhere'])
#
#
#def test_get_with_param():
#    doc = inform.urlopen(root_url).get(page=9)
#    eq_(doc.xpath('//h1/text()'), ["You've reached page #9"])
#
#
#def test_get_with_query_in_action():
#    doc = inform.urlopen(root_url).get_with_query_in_action()
#    eq_(doc.xpath('//h1/text()'), ["You've reached page #9"])
#
#
#def test_get_with_hidden():
#    doc = inform.urlopen(root_url).get_with_hidden()
#    eq_(doc.xpath('//h1/text()'), ["You've reached page #9"])


def test_upload():
    root = inform.urlopen(root_url)
    filename = resource_filename(__name__, 'upload.txt')
    print "RES:", repr(filename)
    doc = root.upload(content=open(filename))


def Xtest_delete_page_9():
    inform.urlopen(root_url).delete_page_9()