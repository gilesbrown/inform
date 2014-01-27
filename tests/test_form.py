# -*- coding: utf-8 -*-
from nose.tools import eq_
import lxml.html
from inform.form import Form
from inform import multipart
from test_multipart import with_fixed_boundary, fixed_boundary


def make_form(html, base_url='http://foo.com/'):
    open_calls = []
    OPENER = object()

    # Just enough mocking
    class Document:
        def __init__(self, request, opener):
            assert opener is OPENER
            if hasattr(request.data, 'read'):
                request_data = []
                while True:
                    more = request.data.read(8192)
                    if not more:
                        break
                    request_data.append(more)
            else:
                request_data = request.data
            open_calls.append((request.get_method(),
                           request.get_full_url(), request_data))

    etree = lxml.html.fromstring(html, base_url=base_url)
    form = Form(etree.forms[0], Document, OPENER)
    return open_calls, form


def test_get_str_param():
    html = '<html><form name="f" action="/get"><input name="s" /></form>'
    calls, form = make_form(html)
    form(s='my string')
    eq_(calls, [('GET', u'http://foo.com/get?s=my+string', None)])


def test_get_unicode_param():
    html = '<html><form name="f" action="/get"><input name="u" /></form>'
    calls, form = make_form(html)
    form(u=u'G\xc9NIFIQUE')
    eq_(calls, [('GET', u'http://foo.com/get?u=G%C3%89NIFIQUE', None)])


def test_get_int_param():
    html = '<html><form name="f" action="/get"><input name="i" /></form>'
    calls, form = make_form(html)
    form(i=3)
    eq_(calls, [('GET', u'http://foo.com/get?i=3', None)])


def test_get_no_params():
    html = '<html><form name="example" action="/get"></form>'
    calls, form = make_form(html)
    form()
    eq_(calls, [('GET', u'http://foo.com/get', None)])


def test_get_uppercase_method():
    html = '''<form name="f" action="/get" method="GET"></form>'''
    calls, form = make_form(html)
    form()
    eq_(calls, [('GET', u'http://foo.com/get', None)])


def test_post_str_param():
    html = '''
      <form name="f" action="/post" method="POST">
        <input name="s" />
      </form>
    '''
    calls, form = make_form(html)
    form(s='Something')
    eq_(calls, [('POST', u'http://foo.com/post', 's=Something')])


@with_fixed_boundary
def test_post_str_param_multipart():
    html = '''
      <form name="f" action="/post" method="POST"
          enctype="multipart/form-data">
        <input name="s" />
      </form>
    '''
    calls, form = make_form(html)
    form(s='Something')
    request_data = [
        multipart.CRLF.join([
            '--' + fixed_boundary,
            'Content-Disposition: form-data; name="s"',
            'Content-Type: text/plain',
            '',
            'Something',
            '--' + fixed_boundary + '--',
            ''
        ])
    ]
    eq_(calls, [('POST', u'http://foo.com/post', request_data)])
