#!/bin/bash

PATH_FOTOBOX="/home/pi/git/fotobox"
LOG_DATE"date +%y%m%d-%H%M"
cd $PATH_FOTOBOX
mkdir -p $PATH_FOTOBOX/log

sudo python $PATH_FOTOBOX/lib/led_server.py > $PATH_FOTOBOX/log/led_server_$LOG_DATE.log 2> $PATH_FOTOBOX/log/led_server_$LOG_DATE.err &
PID=$!

python $PATH_FOTOBOX/fotobox.py > $PATH_FOTOBOX/log/fotobox_$LOG_DATE.log 2> $PATH_FOTOBOX/log/fotobox_$LOG_DATE.err
RETURN=$?

sudo kill $PID

# Shutdown
if [[ $RETURN -eq 12 ]]; then
  sudo shutdown -h now
fi
