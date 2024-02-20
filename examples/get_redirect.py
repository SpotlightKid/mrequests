"""Make various GET requests to httpbin.org to test redirection support."""

import sys
import mrequests


print("Running on platform:", sys.platform)

host = "http://httpbin.org/"
base_url = host + "redirect/"

url = base_url + "1"
print("Requesting %s with default max_redirects ..." % url)
r = mrequests.get(url)
print("Status code:", r.status_code)
r.close()

url = base_url + "2"
print("Requesting %s with default max_redirects=2 ..." % url)
r = mrequests.get(url, max_redirects=2)
print("Status code:", r.status_code)
r.close()

# max_redirects defaults to 1, so this should raise a ValueError
print("Requesting %s with default max_redirects (should fail)..." % url)
try:
    r = mrequests.get(url)
except ValueError as exc:
    print("FAIL", exc)
else:
    r.close()

base_url = host + "absolute-redirect/"

url = base_url + "1"
print("Requesting %s with default max_redirects ..." % url)
r = mrequests.get(url)
print("Status code:", r.status_code)
r.close()

url = base_url + "2"
print("Requesting %s with default max_redirects=2 ..." % url)
r = mrequests.get(url, max_redirects=2)
print("Status code:", r.status_code)
r.close()

# max_redirects defaults to 1, so this should raise a ValueError
print("Requesting %s with default max_redirects (should fail)..." % url)
try:
    r = mrequests.get(url)
except ValueError as exc:
    print("FAIL", exc)
else:
    r.close()
