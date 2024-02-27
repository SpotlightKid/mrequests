#!/bin/bash
#
# Install mrequests to a MicroPython board using mpremote

PKG="mrequests"
MODULES=('__init__.py' 'mrequests.py' 'urlencode.py' 'urlparseqs.py' 'urlunquote.py')
MPYDIR="build/$PKG"
DESTDIR="${DESTDIR:-:/lib}"

mkdir -p "$MPYDIR"
# Create the installation directory
# Will generate errors in the output if it already exists
#
# Traceback (most recent call last):
#   File "<stdin>", line 2, in <module>
# OSError: [Errno 17] EEXIST
mpremote ${PORT:+connect $PORT} mkdir "${DESTDIR}"
mpremote ${PORT:+connect $PORT} mkdir "${DESTDIR}/$PKG"

for py in ${MODULES[*]}; do
    mpy="${py%.*}.mpy"
    echo "Compiling $PKG/$py to $MPYDIR/$mpy"
    ${MPY_CROSS:-mpy-cross} -o "$MPYDIR/$mpy" "$PKG/$py"
    mpremote ${PORT:+connect $PORT} cp "$MPYDIR/$mpy" "$DESTDIR/$PKG/$mpy"
done
