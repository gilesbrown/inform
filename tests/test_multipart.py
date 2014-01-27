from string import ascii_lowercase
from contextlib import closing
from tempfile import NamedTemporaryFile
from StringIO import StringIO
from nose.tools import eq_, with_setup
from inform.form import FormData, FileValue
from inform import multipart

fixed_boundary = '1bcd71449e634565a1a4d295c0255f43'
multipart_generate_boundary = multipart.generate_boundary


def generate_fixed_boundary():
    return fixed_boundary


def setup_fixed_boundary():
    multipart.generate_boundary = generate_fixed_boundary


def teardown_fixed_boundary():
    multipart.generate_boundary = multipart_generate_boundary


with_fixed_boundary = with_setup(setup_fixed_boundary,
                                  teardown_fixed_boundary)


def test_part():
    part = multipart.Part(FormData(b'a', 'b'))
    pieces = list(part.pieces(8192))
    eq_(len(pieces), 5)
    expected_pieces = [
        'Content-Disposition: form-data; name="a"\r\n',
        'Content-Type: text/plain\r\n',
        '\r\n',
        'b',
        '\r\n',
    ]
    eq_(pieces, expected_pieces)
    eq_(len(part), sum(map(len, expected_pieces)))


def test_part_read():
    size_hint = 6
    part = multipart.Part(FormData(b'a',
                                FileValue(StringIO(ascii_lowercase))))
    pieces = list(part.pieces(size_hint))
    eq_(len(pieces), 9)
    expected_pieces = [
        'Content-Disposition: form-data; name="a"\r\n',
        'Content-Type: application/octet-stream\r\n',
        '\r\n',
        # look we get pieces of length 'size_hint'
        'abcdef',
        'ghijkl',
        'mnopqr',
        'stuvwx',
        'yz',
        '\r\n'
    ]
    eq_(pieces, expected_pieces)


def test_part_read_with_len():

    with closing(NamedTemporaryFile()) as tmp:
        tmp.write(ascii_lowercase)
        tmp.flush()
        tmp.seek(0)
        size_hint = 6
        part = multipart.Part(FormData(b'a', FileValue(tmp)))
        pieces = list(part.pieces(size_hint))
        eq_(len(pieces), 9)
        expected_pieces = [
            #'Content-Disposition: form-data; name="a"\r\n',
            'Content-Type: application/octet-stream\r\n',
            '\r\n',
            # look we get pieces of length 'size_hint'
            'abcdef',
            'ghijkl',
            'mnopqr',
            'stuvwx',
            'yz',
            '\r\n'
        ]
        # We don't try and compare content disposition
        eq_(pieces[1:], expected_pieces)
        eq_(len(part), sum(map(len, pieces)))


@with_fixed_boundary
def test_multipart_form_data():
    data = [FormData('n1', 'v1')]
    multipart_form_data = multipart.MultipartFormData(data)
    content = multipart_form_data.read()
    lines = content.split('\r\n')
    expected_lines = [
        '--1bcd71449e634565a1a4d295c0255f43',
        'Content-Disposition: form-data; name="n1"',
        'Content-Type: text/plain',
        '',
        'v1',
        '--1bcd71449e634565a1a4d295c0255f43--',
        '',
    ]
    eq_(lines, expected_lines)
