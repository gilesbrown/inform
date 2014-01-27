from nose.tools import eq_, raises
from StringIO import StringIO
from string import ascii_lowercase
from inform.chunkedtransfer import ChunkedTransferEncoding, read_sizes

CRLF = b'\r\n'


def check_chunk(chunk):
    hex_chunk_size, _, remainder = chunk.partition(CRLF)
    chunk_size = int(hex_chunk_size, 16)
    eq_(remainder[-2:], CRLF)
    eq_(chunk_size, len(remainder[:-2]))
    return chunk_size, remainder[:-2]


def read(size, expected_size, expected_chunk_size, msg=ascii_lowercase * 2):
    chunked = ChunkedTransferEncoding(StringIO(msg))
    bytes_read = chunked.read(size)
    eq_(len(bytes_read), expected_size)
    chunk_size, chunk = check_chunk(bytes_read)
    eq_(chunk, msg[:chunk_size])
    eq_(chunk_size, expected_chunk_size)


@raises(ValueError)
def test_read_size_too_small():
    read(5, 5, 1)


def test_read_size_min():
    read(6, 6, 1)


def test_read_size_just_below_boundary():
    # We can't read exactly 21 bytes because it means
    # we need to start using two hex digits and that
    # means we've already used our extra byte.
    read(21, 20, 15)


def test_read_size_on_boundary():
    read(22, 22, 16)


def test_read_whole_message():
    # 58 = 26 * 2 + 2 + CRLF * 2
    read(512, 58, 52)


def test_read_size_max():
    # We never read more than this
    expected_size = read_sizes[-1]
    expected_chunk_size = expected_size - len('%X' % expected_size) - 4
    read(4294967296L, expected_size, expected_chunk_size, 'Z' * (16 ** 7))
