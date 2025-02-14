#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

"$DIR"/install-pyenv.sh
# ~/.pyenv/shims/python3.6 "$DIR"/main.py --install-y
python "$DIR"/main.py --install-y
