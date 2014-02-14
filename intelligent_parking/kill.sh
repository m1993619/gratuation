#! /bin/bash
pid=$(ps aux | grep $1 | grep -v grep | grep -v kill.sh| awk '{print $2}'|head -1)
if [[ -n $pid ]]; then
    echo kill $1 pid=$pid
    kill -9 $pid
else
    echo $1" Does not exist"
fi
