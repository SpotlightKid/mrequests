#!/bin/bash
#
# Install mrequests to a MicroPython board

PKG="mrequests"
MODULES=('__init__.py' 'mrequests.py' 'urlencode.py' 'urlparseqs.py' 'urlunquote.py')
MPYDIR="build/$PKG"
RSHELL_CMD="${RSHELL:-rshell} --quiet -b ${BAUD:-9600} -p ${PORT:-/dev/ttyACM0}"

mkdir -p "$MPYDIR"
# Create the installation directory
# Will generate errors in the output if it already exists
$RSHELL_CMD mkdir /pyboard/lib
$RSHELL_CMD mkdir /pyboard/$PKG

for py in ${MODULES[*]}; do
    mpy="${py%.*}.mpy"
    echo "Compiling $PKG/$py to $MPYDIR/$mpy"
    ${MPY_CROSS:-mpy-cross} -o "$MPYDIR/$mpy" "$PKG/$py"
    $RSHELL_CMD cp "$MPYDIR/$mpy" "${DESTDIR:-/pyboard/lib}/$PKG"
done
