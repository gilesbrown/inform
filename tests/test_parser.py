from nose.tools import eq_, ok_
from inform.parser import InformParser


class DummyResponse(object):

    def __init__(self, url, content):
        self.url = url
        self.content = content


class DummySession(object):

    def __init__(self, content):
        self.content = content

    def request(self, method, url, params=None, data=None, headers=None):
        # For these tests we're not really concerned about these values
        eq_(method, 'GET')
        eq_(url, URL)
        eq_(params, None)
        eq_(data, None)
        eq_(headers, None)
        return DummyResponse(url, self.content)


def names(obj):
    return set([name for name in dir(obj) if not name.startswith('_')])

SITE = 'http://some.com'
PATH = '/here'
URL = 'http://some.com/here'

def parse(content, names_expected):
    parser = InformParser(DummySession(content))
    res = parser.request('GET', URL)
    ok_(isinstance(res.response, DummyResponse))
    eq_(names(res), set(names_expected))
    return res


def test_empty():
    parse('', ['response'])


def test_minimal_form():
    res = parse('<form id="f1" />', ['response', 'f1'])
    eq_(res.f1.method, 'GET')
    eq_(res.f1.action, URL)
    eq_(res.f1.enctype, None)
   
    
def test_form_enctype():
    res = parse('<form id="f1" method="POST" enctype="multipart/form-data" />', 
                ['response', 'f1'])
    eq_(res.f1.method, 'POST')
    eq_(res.f1.action, URL)
    eq_(res.f1.enctype, 'multipart/form-data')
   
    
def test_form_method_replacement():
    res = parse('<form id="f1" method="POST" action="?_method=DELETE&x=1" />', 
                ['response', 'f1'])
    eq_(res.f1.method, 'DELETE')
    eq_(res.f1.action, URL + '?_method=DELETE&x=1')


def test_minimal_input():
    res = parse('<form id="f1"><input name="i1" /></form>', ['response', 'f1'])
    (input0,) = res.f1.inputs
    eq_(input0.name, 'i1')
    eq_(input0.type, None)
    eq_(input0.value, None)


def test_minimal_link():
    res = parse('<a id="a1" />', ['response', 'a1'])
    eq_(res.a1.href, URL)