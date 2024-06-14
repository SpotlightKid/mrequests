"""A HTTP client module for MicroPython with an API similar to requests."""

import sys

try:
    import socket
except ImportError:
    import usocket as socket


MICROPY = sys.implementation.name == "micropython"
MAX_READ_SIZE = 4 * 1024


def encode_basic_auth(user, password):
    try:
        from binascii import b2a_base64
    except ImportError:
        from ubinascii import b2a_base64

    auth_encoded = b2a_base64(b"%s:%s" % (user, password)).rstrip(b"\n")
    return {b"Authorization": b"Basic %s" % auth_encoded}


def head(url, **kw):
    return request("HEAD", url, **kw)


def get(url, **kw):
    return request("GET", url, **kw)


def post(url, **kw):
    return request("POST", url, **kw)


def put(url, **kw):
    return request("PUT", url, **kw)


def patch(url, **kw):
    return request("PATCH", url, **kw)


def delete(url, **kw):
    return request("DELETE", url, **kw)


def parse_url(url):
    port = None
    host = None

    # str.partition() would be handy here,
    # but it's not supported on the esp8266 port
    delim = url.find("//")
    if delim >= 0:
        scheme, loc = url[:delim].rstrip(':'), url[delim+2:]
    else:
        loc = url
        scheme = ""

    psep = loc.find("/")
    if psep == -1:
        if scheme:
            host = loc
            path = "/"
        else:
            path = loc
    elif psep == 0:
        path = loc
    else:
        path = loc[psep:]
        host = loc[:psep]

    if host:
        hsep = host.rfind(":")

        if hsep > 0:
            port = int(host[hsep + 1 :])
            host = host[:hsep]

    return scheme or None, host, port, path


class RequestContext:
    def __init__(self, url, method=None):
        self.redirect = False
        self.method = method or "GET"
        self.scheme, self.host, self._port, self.path = parse_url(url)
        if not self.scheme or not self.host:
            raise ValueError("An absolute URL is required.")

    @property
    def port(self):
        return self._port if self._port is not None else 443 if self.scheme == "https" else 80

    @property
    def url(self):
        return "%s://%s%s" % (
            self.scheme,
            self.host if self._port is None else ("%s:%s" % (self.host, self.port)),
            self.path,
        )

    def set_location(self, status, location):
        if status in (301, 302, 307, 308):
            self.redirect = True
        elif status == 303 and self.method != "GET":
            self.redirect = True

        if self.redirect:
            scheme, host, port, path = parse_url(location)

            if scheme and self.scheme == "https" and scheme != "https":
                self.redirect = False
                return

            if status not in (307, 308) and self.method != "HEAD":
                self.method = "GET"

            if scheme:
                self.scheme = scheme
            if host:
                self.host = host
                self._port = port

            if path.startswith("/"):
                self.path = path
            else:
                self.path = self.path.rsplit("/", 1)[0] + "/" + path


class Response:
    def __init__(self, sock, sockfile, save_headers=False):
        self._cached = None
        self._chunk_size = 0
        self._content_size = 0
        self._sf = sockfile
        self._sock = sock
        self.chunked = False
        self.encoding = "utf-8"
        self.headers = [] if save_headers else None
        self.reason = ""
        self.status_code = None

    def read(self, size=MAX_READ_SIZE):
        sf = self._sf

        if self.chunked:
            if self._chunk_size == 0:
                l = sf.readline().strip()

                if not l:
                    return b''

                # ignore chunk extensions
                l = l.split(b";", 1)[0]
                self._chunk_size = max(0, int(l, 16))

                if self._chunk_size == 0:
                    # End of message
                    sep = sf.read(2)

                    if sep != b"\r\n":
                        raise ValueError("Expected final chunk separator, read %r instead." % sep)

                    return b""

            data = sf.read(min(size or MAX_READ_SIZE, self._chunk_size))
            self._chunk_size = max(0, self._chunk_size - len(data))

            if self._chunk_size == 0:
                sep = sf.read(2)
                if sep != b"\r\n":
                    raise ValueError("Expected chunk separator, read %r instead." % sep)

            return data
        else:
            return sf.read(size if size else self._content_size)

    def readinto(self, buf, size=0):
        if size:
            return self._sf.readinto(buf, size)
        else:
            return self._sf.readinto(buf)

    def save(self, fn, buf=None, chunk_size=0):
        with open(fn, "wb") as fobj:
            return self.saveinto(fobj, buf, chunk_size)

    def saveinto(self, fobj, buf=None, chunk_size=0):
        num_read_total = 0

        if buf:
            if self.chunked:
                raise NotImplementedError("Cannot use a buffer when saving a chunked response.")
            if chunk_size and not MICROPY:
                raise NotImplementedError("Cannot set chunk_size when using a buffer with CPython."
                    " Use a buffer or memoryview of appropriate size instead.")

        remain = self._content_size

        while True:
            if buf:
                num_read_chunk = self.readinto(buf, chunk_size)

                if not num_read_chunk:
                    break

                num_read_total += num_read_chunk
                fobj.write(buf[:num_read_chunk])
            else:
                # Read a chunk of data
                chunk = self.read(size=None if self.chunked
                                  else min(chunk_size or MAX_READ_SIZE, remain))
                num_read_total += len(chunk)

                if not chunk:
                    break

                fobj.write(chunk)

            if not self.chunked:
                remain = self._content_size - num_read_total

                if remain <= 0:
                    break

    def _parse_header(self, data):
        if data[:18].lower() == b"transfer-encoding:" and b"chunked" in data[18:]:
            self.chunked = True
            # print("Chunked response detected.")
        elif data[:15].lower() == b"content-length:":
            self._content_size = int(data[15:])
            # print("Content length: %i" % self._content_size)
        elif data[:17].lower() == b"content-encoding:":
            self.encoding = data[17:].decode().strip()

    # overwrite this method, if you want to process/store headers differently
    def add_header(self, data):
        self._parse_header(data)

        if self.headers is not None:
            self.headers.append(data.rstrip(b"\r\n"))

    def close(self):
        if self._sf and not MICROPY:
            self._sf.close()
            self._sf = None
        if self._sock:
            self._sock.close()
            self._sock = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.read(size=None)
            finally:
                self._sock.close()
                self._sock = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        try:
            import json
        except ImportError:
            import ujson as json

        return json.loads(self.content)


def request(
    method,
    url,
    data=None,
    json=None,
    headers={},
    auth=None,
    encoding=None,
    response_class=Response,
    save_headers=False,
    max_redirects=1,
    timeout=None,
    ssl_context=None
):
    if auth:
        headers.update(auth if callable(auth) else encode_basic_auth(auth[0], auth[1]))

    if json is not None:
        assert data is None
        try:
            import json
        except ImportError:
            import ujson as json

        data = json.dumps(json)

    ctx = RequestContext(url, method)

    while True:
        if ctx.scheme not in ("http", "https"):
            raise ValueError("Protocol scheme %s not supported." % ctx.scheme)

        ctx.redirect = False

        # print("Resolving host address...")
        ai = socket.getaddrinfo(ctx.host, ctx.port, 0, socket.SOCK_STREAM)[0]

        # print("Creating socket...")
        sock = socket.socket(ai[0], ai[1], ai[2])
        sock.settimeout(timeout)
        try:
            # print("Connecting to %s:%i..." % (ctx.host, ctx.port))
            sock.connect(ai[-1])
            if ctx.scheme == "https":
                try:
                    import tls as ssl
                except ImportError:
                    try:
                        import ssl
                    except ImportError:
                        import ussl as ssl


                # print("Wrapping socket with TLS")
                if ssl_context is None:
                    if hasattr(ssl, "create_default_context"):
                        ssl_context = ssl.create_default_context()
                    else:
                        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                        if hasattr(ssl, "CERT_OPTIONAL"):
                            ssl_context.verify_mode = ssl.CERT_OPTIONAL

                sock = ssl_context.wrap_socket(sock, server_hostname=ctx.host)

            sf = sock if MICROPY else sock.makefile("rwb")
            sf.write(b"%s %s HTTP/1.1\r\n" % (ctx.method.encode("ascii"), ctx.path.encode("ascii")))
            sf.write(b"Host: %s\r\n" % headers.get(b"Host", ctx.host.encode()))

            for k, val in headers.items():
                if not isinstance(k, bytes):
                    k = k.encode("ascii")

                if k.lower() == b"host":
                    continue

                sf.write(k)
                sf.write(b": ")
                sf.write(val if isinstance(val, bytes) else val.encode("ascii"))
                sf.write(b"\r\n")

            if data and ctx.method not in ("GET", "HEAD"):
                if json is not None:
                    sf.write(b"Content-Type: application/json")
                    if encoding:
                        sf.write(b"; charset=%s" % encoding.encode())
                    sf.write(b"\r\n")

                sf.write(b"Content-Length: %d\r\n" % len(data))

            sf.write(b"Connection: close\r\n\r\n")

            if data and ctx.method not in ("GET", "HEAD"):
                sf.write(data if isinstance(data, bytes) else data.encode(encoding or "utf-8"))

            if not MICROPY:
                sf.flush()

            resp = response_class(sock, sf, save_headers=save_headers)
            l = b""
            while True:
                l += sf.read(1)

                if l.endswith(b"\r\n") or len(l) > MAX_READ_SIZE:
                    break

            # print("Response: %s" % l.decode("ascii"))
            l = l.split(None, 2)
            resp.status_code = int(l[1])

            if len(l) > 2:
                resp.reason = l[2].rstrip()

            while True:
                l = sf.readline()
                if not l or l == b"\r\n":
                    break

                if l.startswith(b"Location:"):
                    ctx.set_location(resp.status_code, l[9:].strip().decode("ascii"))

                # print("Header: %r" % l)
                resp.add_header(l)
        except OSError:
            if not MICROPY:
                try:
                    sf.close()
                    del sf
                except:
                    pass
            sock.close()
            del sock
            raise

        if ctx.redirect:
            # print("Redirect to: %s" % ctx.url)
            if not MICROPY:
                try:
                    sf.close()
                    del sf
                except:
                    pass
            sock.close()
            del sock
            max_redirects -= 1

            if max_redirects < 0:
                raise ValueError("Maximum redirection count exceeded.")
        else:
            break

    return resp
