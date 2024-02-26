"""Send GET HTTP request and request and handle 'deflate' compression of response.

Requires the 'deflate' module added in Micropython v1.21, the 'zlib' module from
micropython-lib, or the CPython standard library.

"""

try:
    # Use MicroPython's 'deflate' module, if available,
    # to avoid dependency on and RAM cost of 'zlib' module.
    import deflate
except ImportError:
    import zlib

    def decompress(resp):
        return zlib.decompress(resp.content)
else:
    def decompress(resp, wbits=10):
        with deflate.DeflateIO(resp._sf, deflate.ZLIB, wbits) as g:
            return g.read()

import mrequests


host = "http://httpbin.org/"
# host = "http://localhost/"
url = host + "deflate"
r = mrequests.get(url, headers={b"TE": b"deflate"}, save_headers=True)

if r.status_code == 200:
    print("Response headers:")
    print("-----------------\n")
    print(b"\n".join(r.headers).decode())

    if r.encoding.split(",")[0] == "deflate":
        text = decompress(r).decode("utf-8")
        print("Deflated response text length: %i" % len(text))
    else:
        text = r.text

    print("Response text:")
    print("--------------\n")
    print(text)
else:
    print("Request failed. Status: {}".format(r.status_code))

r.close()
