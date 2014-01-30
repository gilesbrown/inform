from contextlib import contextmanager
from collections import OrderedDict
from nose.tools import eq_
from inform.representation import Form, Input, Select, MISSING


class DummyParser(object):

    def __init__(self):
        self.requests = []

    def request(self, method, action, params=None, data=None, headers=None):
        self.requests.append((method, action, params, data, headers))
        
# Testing strategy for inform.representation is to test at Form level.

@contextmanager
def form(inputs=[], **form_kwargs):
    parser = DummyParser()
    form = Form(parser, inputs, **form_kwargs)
    def request(**kw):
        form(**kw)
        requested = parser.requests.pop()
        assert not parser.requests
        return requested
    yield request
        

def test_form():
    with form() as call:
        eq_(call(), ('GET', '', [], None, None))
   

def test_form_select():
    options = OrderedDict([('o2', '2'), ('o1', '1')])
    inputs = [Select('s', options, ['o2'])]
    with form(inputs) as call:
        eq_(call(), ('GET', '', [('s', '2')], None, None))

    
def test_form_select_with_string():
    options = OrderedDict([('o2', '2'), ('o1', '1')])
    inputs = [Select('s', options, ['o2'])]
    with form(inputs) as call:
        eq_(call(s='o1'), ('GET', '', [('s', '1')], None, None))
    

def test_form_select_multiple():
    options = OrderedDict([('o2', '2'), ('o1', '1')])
    inputs = [Select('s', options, ['o2'])]
    with form(inputs) as call:
        eq_(call(s=['o1', 'o2']), ('GET', '', [('s', '1'), ('s', '2')], None, None))
    

def test_form_select_no_default():
    options = OrderedDict([('o2', '2'), ('o1', '1')])


def test_form_select_no_default():
    options = OrderedDict([('o2', '2'), ('o1', '1')])
    inputs = [Select('s', options)]
    with form(inputs) as call:
        eq_(call(), ('GET', '', [], None, None))
        