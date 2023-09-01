import mrequests

buf = memoryview(bytearray(1024))

host = 'http://httpbin.org/'
#host = "http://localhost/"
url = host + "image"
filename = "image.png"
r = mrequests.get(url, headers={b"accept": b"image/png"})

if r.status_code == 200:
    r.save(filename, buf=buf)
    print("Image saved to '{}'.".format(filename))
else:
    print("Request failed. Status: {}".format(r.status_code))

r.close()
