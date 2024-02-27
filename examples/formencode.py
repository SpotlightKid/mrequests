"""Send a POST request with a form-encoded data in the request body."""

import mrequests


def request(method, url, data=None, json=None, headers=None, encoding=None):
    if isinstance(data, dict):
        from mrequests.urlencode import urlencode

        if headers is None:
            headers = {}

        headers[b"Content-Type"] = "application/x-www-form-urlencoded"
        data = urlencode(data, encoding=encoding)

    return mrequests.request(method, url, data=data, json=json, headers=headers)


if __name__ == "__main__":
    import sys

    host = "http://httpbin.org/"
    url = host + "post"
    data = dict((arg.split("=") for arg in sys.argv[1:]))
    r = request("POST", url, data=data)

    if r.status_code == 200:
        print(r.json())
    else:
        print("Request failed. Status: {}".format(r.status_code))

    r.close()
