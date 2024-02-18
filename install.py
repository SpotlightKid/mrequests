#!/usr/bin/env python3
"""Install a set of modules to a MicroPython board using mpremote.

The modules to be installed are read from a file named 'package.json', which should look like this:

    {
        "urls": [
            ["dest/file.py", "github:org/repo/file.py"],
            ...
        ]
    }

See also: https://docs.micropython.org/en/latest/reference/packages.html#writing-publishing-packages

"""

import argparse
import hashlib
import json
import os
import sys

from os.path import join, splitext
from posixpath import join as pjoin, split as psplit
from subprocess import run
from urllib.parse import urlparse

from mpremote.main import State, argparse_filesystem
from mpremote.commands import do_connect, do_disconnect, do_filesystem


HASH_CMD = """\
import binascii, gc, hashlib
h = hashlib.sha256()
try:
 with open('{path}', 'rb') as f:
  while 1:
   d = f.read(1024)
   if not d:
    break
   h.update(d)
 print(binascii.hexlify(h.digest()).decode())
except: pass
del h
gc.collect()
"""

MAKEDIRS_CMD = """\
import os
parts = '{path}'.split('/')
dirs = []
while 1:
 if not parts:
  break
 dirs.append(parts.pop(0))
 dst = "/".join(dirs)
 try:
  os.stat(dst)
 except OSError:
  os.mkdir(dst)
"""


def file_hash(path):
    with open(path, "rb") as fp:
        return hashlib.file_digest(fp, "sha256").hexdigest()


def mp_hash(state, path):
    state.transport.enter_raw_repl()
    ret = state.transport.exec(HASH_CMD.format(path=path).encode("utf-8"))
    state.transport.exit_raw_repl()
    return ret.decode("ascii").strip()


def mp_makedirs(state, path):
    state.transport.enter_raw_repl()
    state.transport.exec(MAKEDIRS_CMD.format(path=path).encode("utf-8"))
    state.transport.exit_raw_repl()


def mp_copy_file(state, src, dst):
    args = argparse_filesystem().parse_args(["cp", src, dst])
    do_filesystem(state, args)


def do_install():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "-d",
        "--target",
        default=":/lib",
        help="Destination directory on device (default: ':/lib')",
    )
    ap.add_argument(
        "-b",
        "--builddir",
        default="build",
        help="Local directory for compiled .mpy modules (default: 'build')",
    )
    ap.add_argument(
        "-n",
        "--no-mpy",
        action="store_true",
        help="Don't compile modules with mpy-cross and install .py files instead",
    )
    ap.add_argument(
        "device",
        nargs="?",
        default=["auto"],
        help=(
            "Device of MicroPython board to install to. "
            "Either list, auto, id:x, port:x, or any valid device name/path (default: 'auto')"
        ),
    )
    args = ap.parse_args()

    try:
        with open("package.json") as fp:
            modules = json.load(fp)["urls"]
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(
            "Could not read/parse 'package.json'. "
            "It must contain valid JSON with a module definition having an 'urls' key.\n"
            f"{exc}"
        )

    state = State()
    do_connect(state, args)

    if args.target.startswith(":"):
        mp_makedirs(state, args.target[1:])
    else:
        os.makedirs(args.target, exist_ok=True)

    for dest, url in modules:
        if url.startswith("github:"):
            src_path = url[7:].split("/")
            src_path = "/".join(src_path[2:])
        else:
            src_path = urlparse(url).path.split("/")[-1]

        dest_path, dest_fn = psplit(dest)

        if not args.no_mpy:
            dest_fn = splitext(dest_fn)[0] + ".mpy"

        target_path = pjoin(args.target, dest_path, dest_fn)

        if target_path.startswith(":"):
            dest_hash = mp_hash(state, target_path[1:])
        else:
            dest_hash = file_hash(target_path)

        if not args.no_mpy:
            os.makedirs(join(args.builddir, dest_path), exist_ok=True)
            src = join(args.builddir, dest_path, dest_fn)
            run(["mpy-cross", "-o", src, src_path])
        else:
            src = src_path

        if not dest_hash or file_hash(src) != dest_hash:
            if dest_path:
                target_dir = pjoin(args.target.lstrip(":"), dest_path)
                mp_makedirs(state, target_dir)

            mp_copy_file(state, src, target_path)
        else:
            print(f"{target_path}: up-to-date")

    do_disconnect(state)


if __name__ == "__main__":
    do_install()
