"""Make various GET requests to httpbin.org to test redirection support."""

import sys
import mrequests


def main():
    print("Running on platform:", sys.platform)

    host = "http://httpbin.org/"
    base_url = host + "redirect/"

    url = base_url + "1"
    print("Requesting %s with default max_redirects ..." % url)
    r = mrequests.get(url)
    print("Status code:", r.status_code)
    r.close()

    url = base_url + "2"
    print("Requesting %s with max_redirects=2 ..." % url)
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
    print("Requesting %s with max_redirects=2 ..." % url)
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
        print("Status code:", r.status_code)
        r.close()

    url = base_url.replace("http:", "https:") + "1"
    print("Requesting HTTPS URL %s redirecting to HTTP location (should NOT follow redirect)..." % url)
    r = mrequests.get(url, save_headers=True)
    print("Status code:", r.status_code)
    for hline in r.headers:
        if hline.startswith(b"Location:"):
            print("Location:", hline.decode("ascii").split(":", 1)[1].strip())

    r.close()


if __name__ == '__main__':
    main()
