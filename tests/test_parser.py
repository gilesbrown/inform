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
    res = parse('<form id="f1" method="POST" action="?_method=delete&x=1" />', 
                ['response', 'f1'])
    eq_(res.f1.method, 'DELETE')
    eq_(res.f1.action, URL + '?_method=delete&x=1')


def test_minimal_input():
    res = parse('<form id="f1"><input name="i1" /></form>', ['response', 'f1'])
    (input0,) = res.f1.inputs
    eq_(input0.name, 'i1')
    eq_(input0.type, None)
    eq_(input0.default, None)
   
    
def test_input_default():
    res = parse('<form id="f1"><input name="i0" value="v"/></form>', ['response', 'f1'])
    (i0,) = res.f1.inputs
    eq_(i0.name, 'i0')
    eq_(i0.type, None)
    eq_(i0.default, 'v')


def test_minimal_select():
    res = parse('<form id="f1"><select name="s"><option>a</option><option>b</option></select></form>', ['response', 'f1'])
    (s,) = res.f1.inputs
    eq_(s.name, 's')
    eq_(s.options.items(), [('a', 'a'), ('b', 'b')])

    
def test_select_single_selected():
    res = parse("""
      <form id="f1">
        <select name="s">
          <option>a</option>
          <option selected="selected">b</option>
        </select>
      </form>
    """, ['response', 'f1'])
    (s,) = res.f1.inputs
    eq_(s.name, 's')
    eq_(s.options.items(), [('a', 'a'), ('b', 'b')])
    eq_(s.default, ['b'])
    
def test_select_multiple_selected():
    res = parse("""
      <form id="f1">
        <select name="s">
          <option selected="selected">b</option>
          <option>a</option>
          <option selected="selected">c</option>
        </select>
      </form>
    """, ['response', 'f1'])
    (s,) = res.f1.inputs
    eq_(s.name, 's')
    eq_(s.options.items(), [('b', 'b'), ('a', 'a'), ('c', 'c')])
    eq_(s.default, ['b', 'c'])


def test_minimal_link():
    rep1 = parse('<a id="a1" />', ['response', 'a1'])
    eq_(rep1.a1, URL)
    # we should be able to follow the link and get a new Representation
    rep2 = rep1.a1()
    eq_(rep2.a1, rep1.a1)


def test_value():
    rep1 = parse('<code id="v0">1</code>', ['response', 'v0'])
    eq_(rep1.v0, '1')
   
    
def test_value_typed():
    rep1 = parse('<code id="v0" class="json">1</code>', ['response', 'v0'])
    eq_(rep1.v0, 1)
   
    
def test_ul():
    rep1 = parse("""
      <ul id="v0">
        <li>item1</li>
      </ul>
    """, ['response', 'v0'])
    eq_(rep1.v0, ['item1'])
    
    
def test_ol():
    rep1 = parse('<ol id="v0"><li>item1</li></ol>', 
                 ['response', 'v0'])
    eq_(rep1.v0, ['item1'])
    
    
def test_dl():
    rep1 = parse('<dl id="v0"><dt>k1</dt><dd>v1</dd></dl>', 
                 ['response', 'v0'])
    eq_(rep1.v0, {'k1': 'v1'})
          

def test_dl_nested_a(): 
    rep1 = parse('<dl id="v0"><dt>url</dt><dd><a>k1</a></dd></dl>', 
                 ['response', 'v0'])
    eq_(rep1.v0, {'url': URL})
    # Hey look we can make a request using this new URL
    rep2 = rep1.v0['url']()
    eq_(rep1.response.url, rep2.response.url)