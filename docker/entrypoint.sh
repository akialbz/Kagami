#!/usr/bin/env bash
set -e

if [[ "$#" -eq 0 ]] || [[ ! -f $1 ]]; then
    echo "ERROR: no input file or invalid input file name [[ $1 ]]"
    exit
fi

python "$@"
