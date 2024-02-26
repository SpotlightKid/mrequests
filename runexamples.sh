#!/bin/bash
#
# Run all scripts in examples/ dir with MicroPython unix port, CPython
# or a MicroPython board (via mpremote)
#

if [[ -n "$DEVICE" ]]; then
    if ! which mpremote >&/dev/null; then
        echo "Please install 'mpremote'."
        exit 1
    fi
    mpremote connect "$DEVICE" mip install collections-defaultdict
    ./install.py "$DEVICE" || exit 1
fi

for example in examples/*.py; do
    echo "Running example $example..."
    if [[ -n "$DEVICE" ]]; then
        mpremote \
            connect "$DEVICE" \
            run "$example" "$@"
        ret=$?
    elif [[ -n "$PYTHON" ]]; then
        export PYTHONPATH="$(pwd)"
        "$PYTHON" "$example" "$@"; ret=$?
    else
        export MICROPYPATH="$(pwd):$MICROPYPATH"
        micropython "$example" "$@"; ret=$?
    fi

    if [[ $ret -ne 0 ]]; then
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" >/dev/stderr
        echo "FAIL: $example" >/dev/stderr
    fi
    echo
done
