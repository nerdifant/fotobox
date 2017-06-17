#!/bin/bash

PATH_FOTOBOX="/home/pi/git/fotobox"
cd $PATH_FOTOBOX
mkdir -p $PATH_FOTOBOX/log

sudo python $PATH_FOTOBOX/lib/led_server.py > $PATH_FOTOBOX/log/led_server.log 2> $PATH_FOTOBOX/log/led_server.err &
PID=$!

python $PATH_FOTOBOX/fotobox.py > $PATH_FOTOBOX/log/fotobox.log 2> $PATH_FOTOBOX/log/fotobox.err
RETURN=$?

sudo kill $PID

# Shutdown
if [[ $RETURN -eq 12 ]]; then
  sudo shutdown -h now
fi
