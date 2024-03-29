"""Upload a file via a POST request with a multipart/form-data encoded request body.

This reads the whole file and builds the request body in memory, so this isn't
the most efficient way to do this and will quickly lead to out-of-memory errors
on microcontrollers with restrained memory.

"""

import os
try:
    from binascii import hexlify
except ImportError:
    from ubinascii import hexlify

import mrequests


def create_multipart_request(file=None, filename=None, data=None):
    boundary = hexlify(os.urandom(16))
    lines = []

    if data:
        for name in data:
            lines.append(b"--" + boundary)
            lines.append(b'Content-Disposition: form-data; name="%s"' % name)
            lines.append(b"")
            lines.append(data[name])

    if file is not None:
        lines.append(b"--" + boundary)
        lines.append(b'Content-Disposition: form-data; name="file"; filename="%s"' % (filename))
        lines.append(b"")
        lines.append(file.read())

    lines.append(b"--" + boundary + b"--")
    lines.append(b"")

    return {b"content-type": b"multipart/form-data; boundary=" + boundary}, b"\r\n".join(lines)


def upload_file(url, filename, **kw):
    with open(filename, "rb") as fp:
        if "/" in filename:
            filename = filename.rsplit("/", 1)[1]

        headers, data = create_multipart_request(fp, filename.encode("ascii"), data=kw)

    return mrequests.post(url, headers=headers, data=data)


if __name__ == "__main__":
    import sys

    try:
        url = sys.argv.pop(1)
    except:
        url = "http://httpbin.org/post"

    try:
        filename = sys.argv.pop(1)
    except:
        filename = hexlify(os.urandom(8)).decode() + ".txt"
        with open(filename, "w") as fp:
            fp.write("This is a dummy text file for testing HTTP file upload.\n")

    data = {}
    for arg in sys.argv[3:]:
        k, v = arg.encode().split(b"=")
        data[k] = v

    resp = upload_file(url, filename, **data)

    if resp.status_code in (200, 204):
        print("Sucessfully uploaded file '%s'." % filename)
        print(resp.text)
    else:
        print("Upload failed: %s %s" % (resp.status_code, resp.reason.decode()))

    resp.close()
