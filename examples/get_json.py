"""Send GET request expecting JSON in the response body and print and decode it."""

import mrequests


host = "http://httpbin.org/"
# host = "http://localhost/"
url = host + "get"
r = mrequests.get(url, headers={b"Accept": b"application/json"})
print(r)

if r.status_code == 200:
    print("Raw response body:")
    print(r.content)
    print("Response body decoded to string:")
    print(r.text)
    print("Data from decode from JSON notation in response body:")
    print(r.json())
else:
    print("Request failed. Status: {}".format(r.status_code))

r.close()
