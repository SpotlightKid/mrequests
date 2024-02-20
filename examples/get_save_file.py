"""Send GET request expecting a PNG image in the response body and save it to a file."""

import mrequests


host = "http://httpbin.org/"
# host = "http://localhost/"
url = host + "image"
filename = "image.png"
r = mrequests.get(url, headers={b"Accept": b"image/png"})

if r.status_code == 200:
    r.save(filename)
    print("Image saved to '{}'.".format(filename))
else:
    print("Request failed. Status: {}".format(r.status_code))

r.close()
