import os
from os.path import abspath, dirname, join
from unittest import TestCase, main

from mrequests import request

tests_dir = abspath(dirname(__file__))
TEST_REQUESTS = [
    ("image.png", ("GET", "https://httpbin.org/image/png")),
    ("data.json", ("GET", "https://httpbin.org/json")),
]


class TestRequestContext(TestCase):
    def setUp(self):
        os.makedirs(join(tests_dir, "output"), exist_ok=True)

    def test_read(self):
        for fn, args in TEST_REQUESTS:
            resp = request(*args)
            infn = join(tests_dir, "data", fn)

            self.assertEqual(open(infn, "rb").read(), resp.read(size=None))


    def test_saveinto(self):
        for fn, args in TEST_REQUESTS:
            resp = request(*args)
            infn = join(tests_dir, "data", fn)
            outfn = join(tests_dir, "output", fn)

            with open(outfn, "wb") as fp:
                resp.saveinto(fp)

            self.assertEqual(open(infn, "rb").read(), open(outfn, "rb").read())

if __name__ == '__main__':
    main()
