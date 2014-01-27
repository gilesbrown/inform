""" An HTTP server for use in functional tests. """

import os
import threading
import shutil
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler, test
from pkg_resources import resource_stream
from test.filesystem import url2resource


# maximal line length when calling readline().
_MAXLINE = 65536


def create_server():
    server = HTTPServer(('127.0.0.1', 0), RequestHandler)
    server.thread = threading.Thread(target=server_thread, args=(server,))
    return server


def server_thread(server, *args, **kwargs):
    server.serve_forever(0.1)


class RequestHandler(BaseHTTPRequestHandler):

    __version__ = ''

    server_version = "SimpleHTTP/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        content_length = self.headers.getheader('content-length')
        transfer_encoding = self.headers.getheader('transfer-encoding')
        import sys
        if content_length is not None:
            print "CT:", self.headers.getheader('content-type')
            #print self.rfile.read(int(content_length))
            import cgi
            fs = cgi.FieldStorage(self.rfile, headers=self.headers)
            print "KEYS:", fs.keys()
            #remainder = int(content_length)
            #with open('c:\\work\giles.resp', 'wb') as fp:
            ##    while remainder > 0:
            ##        size = min(remainder, 8192)
            #        fp.write(self.rfile.read(size))
            #        remainder -= size
        elif transfer_encoding == 'chunked':
            #print "IT's CHUNKED!?!?", type(self.rfile)
            for chunk in self.read_chunks():
                sys.stdout.write(chunk)
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_DELETE(self):
        self.send_response(201)
        self.end_headers()

    def read_chunks(self):
        while True:
            chunk_line = self.rfile.readline(_MAXLINE + 1)
            #print "CHUNK LINE: %r" % chunk_line
            if not chunk_line.rstrip():
                continue
            if len(chunk_line) > _MAXLINE:
                raise RuntimeError("chunk size")
            i = chunk_line.find(';')
            if i >= 0:
                chunk_line = chunk_line[:i]  # strip chunk-extensions
            try:
                chunk_size = int(chunk_line, 16)
            except ValueError:
                # close the connection as protocol synchronisation is
                # probably lost
                #self.close()
                raise RuntimeError(repr(chunk_line))
            if chunk_size == 0:
                break
            chunk = self.rfile.read(chunk_size)
            yield chunk

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        resource = url2resource(self.path)
        try:
            f = resource_stream(__name__, resource)
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", 'text/html')
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)


if __name__ == '__main__':
    test(RequestHandler, HTTPServer)
