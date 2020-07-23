#!/usr/bin/env bash
set -e

if [[ $1 == 'python' ]]; then
    python
elif [[ $1 == 'test' ]]; then
    python -c "import kagami; kagami.test()"
elif [[ "$#" -eq 0 ]] || [[ ! -f $1 ]]; then
    echo "ERROR: no input file or invalid input file name [[ $1 ]]"
    exit
else
    python "$@"
fi

