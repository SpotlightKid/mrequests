"""Send GET HTTP request and request and handle 'deflate' compression of response.

Requires the 'zlib' module from micropython-lib or the CPython standard library.

"""

import zlib
import mrequests


host = "http://httpbin.org/"
# host = "http://localhost/"
url = host + "deflate"
r = mrequests.get(url, headers={b"TE": b"deflate"}, save_headers=True)

if r.status_code == 200:
    print("Response headers:")
    print(b"\n".join(r.headers).decode())

    if r.encoding.split(",")[0] == "deflate":
        text = zlib.decompress(r.content).decode("utf-8")
        print("Deflated response text length: %i" % len(text))
    else:
        text = r.text

    print("Response text:")
    print(text)
else:
    print("Request failed. Status: {}".format(r.status_code))

r.close()
