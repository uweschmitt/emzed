#!/bin/sh
echo "dangling python interpreters:"
ps -W | grep -i python.exe
echo
echo "kill them"
ps -W | grep -i python.exe | cut -d" " -f1-12 | xargs /bin/kill -f
