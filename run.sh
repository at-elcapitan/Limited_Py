#! /bin/bash
set -e

echo "Executing: pip install venv"
python3 -m pip install virtualenv

echo "Checking venvl/"
[ ! -d "venvl" ] && echo "venv/ not exists, creating" && python3 -m virtualenv venvl

echo "Entering virtualenv"
source ./venvl/bin/activate

echo "Executing: pip install -r requirements.txt"
python3 -m pip install -r requirements.txt

echo "Starting bot..." 
clear

python3 atlb
