#! /bin/bash
set -e

echo "Executing: pip install venv"
python3 -m pip install virtualenv

echo "Checking venv/"
[ ! -d "venv" ] && echo "venv/ not exists, creating" && python3 -m virtualenv venv

echo "Entering virtualenv"
source ./venv/Scripts/activate

echo "Executing: pip install -r requirements.txt"
python3 -m pip install -r requirements.txt

echo "Starting bot..."
timeout 2s 
clear

python3 atlb