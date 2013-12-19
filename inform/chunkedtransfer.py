from bisect import bisect

EMPTY = b''
FINAL_CHUNK = b'0\r\n\r\n'
# Each chunk is '{size_in_hex}\r\n{chunk}\r\n'
CRLF_X2 = 4
# We don't support reading more than 16 ** 7 bytes at a time
read_sizes = [16 ** i + CRLF_X2 + i + 1 for i in range(8)]


class ChunkedTransferEncoding(object):
    """HTTP/1.1 chunked transfer encoding.

    The objective here to allow Inform clients to be able to send
    multipart/form-data with file uploads incrementally, even when
    the size of the file is not known ahead of time (e.g. the content
    is generated rather than stored in the file system).

    The way we implement this is to act as a file-like object and
    implement a 'read' method.  This is what 'httplib:HTTPConnection.send'
    will call when it needs to ask for more data to send.
    """

    def __init__(self, fp):
        self.fp = fp

    # We have to have this to keep urllib.Request happy
    def __len__(self):
        return 0

    def read(self, size=None):
        if self.fp is None:
            return EMPTY

        if size is None:
            size = 8192

        chunk = self.fp.read(self.chunk_size(size))
        if not chunk:
            return FINAL_CHUNK

        return b'%X\r\n%s\r\n' % (len(chunk), chunk)

    def chunk_size(self, read_size):
        """ Return best chunk size given the requested read size.
        """
        num_hex_chars = bisect(read_sizes, read_size)
        if not num_hex_chars:
            # We can't create a chunk with a size less than 6 bytes
            raise ValueError("'read_size' %r is too small" % read_size)
        # The number of hex chars limits the size of the chunk
        max_chunk_size = 16 ** num_hex_chars - 1
        # Use the read size to determine the chunk size unless this
        # number is bigger than the maximum chunk size.
        # This only happens if the 'read_size' falls on a power of 16
        # or if the read_size is bigger than we allow in a single
        # chunk.
        return min(max_chunk_size, read_size - num_hex_chars - CRLF_X2)
