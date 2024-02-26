"""Example of how to download a file in chunk using a pre-allcoated buffer
and print download progress."""

import sys
import mrequests

buf = bytearray(1024)


class ResponseWithProgress(mrequests.Response):
    _total_read = 0

    def readinto(self, buf, size=0):
        bytes_read = super().readinto(buf, size)
        self._total_read += bytes_read
        print("Progress: {:.2f}%".format(self._total_read / (self._content_size * 0.01)))
        return bytes_read


if len(sys.argv) > 1:
    url = sys.argv[1]

    if len(sys.argv) > 2:
        filename = sys.argv[2]
    else:
        filename = url.rsplit("/", 1)[1]
else:
    host = "http://httpbin.org/"
    # host = "http://localhost/"
    url = host + "image"
    filename = "image.png"

r = mrequests.get(url, headers={b"accept": b"image/png"}, response_class=ResponseWithProgress)

if r.status_code == 200:
    r.save(filename, buf=buf)
    print("Image saved to '{}'.".format(filename))
else:
    print("Request failed. Status: {}".format(r.status_code))

r.close()
