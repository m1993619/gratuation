#! /bin/bash
SCRIPT_ROOT=$(dirname "$0")
cd $SCRIPT_ROOT
./stop.sh
echo 'python wsgi.py 8816 $1 &'
nohup python wsgi.py 8816 $1 &
