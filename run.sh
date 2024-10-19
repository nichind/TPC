# !/bin/bash

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
python_executable=$(which python3.11)
cd $SCRIPTPATH
$python_executable -m venv .venv
source .venv/bin/activate
$python_executable -m pip install --upgrade pip
$python_executable -m pip install -r requirements.txt
$python_executable main.py