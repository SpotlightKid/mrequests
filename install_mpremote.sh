#!/bin/bash
#
# Install mrequests to a MicroPython board

MODULES=('defaultdict.py' 'mrequests.py' 'urlencode.py' 'urlparseqs.py' 'urlunquote.py')
DESTDIR=":/lib/"
for py in ${MODULES[*]}; do
    echo "Compiling $py to ${py%.*}.mpy"
    mpy-cross "$py"
    mpremote cp ${py%.*}.mpy "${DESTDIR}${py%.*}.mpy" 
done
