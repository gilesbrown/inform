from nose.tools import eq_
from inform.representation import Input, Form


class DummyParser(object):

    def __init__(self):
        self.requests = []

    def request(self, method, action, params=None, data=None, headers=None):
        self.requests.append((method, action, params, data, headers))


def test_form():
    parser = DummyParser()
    form = Form(parser, [Input('myinput')])
    form(myinput='hello')
    eq_(parser.requests, [('GET', '', [('myinput', 'hello')], None, None)])
