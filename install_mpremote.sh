#!/bin/bash
#
# Install mrequests to a MicroPython board using mpremote

MODULES=('defaultdict.py' 'mrequests.py' 'urlencode.py' 'urlparseqs.py' 'urlunquote.py')
DESTDIR=":/lib"

# Create the root lib folder
# Will generate an error in the output if it already exists
# 
# Traceback (most recent call last):
#   File "<stdin>", line 2, in <module>
# OSError: [Errno 17] EEXIST
mpremote mkdir "${DESTDIR}"

for py in ${MODULES[*]}; do
    echo "Compiling $py to ${py%.*}.mpy"
    mpy-cross "$py"
    mpremote cp ${py%.*}.mpy "${DESTDIR}/${py%.*}.mpy" 
done
