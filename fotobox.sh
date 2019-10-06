#!/bin/bash

PATH_FOTOBOX="/home/pi/git/fotobox"
cd $PATH_FOTOBOX
python $PATH_FOTOBOX/setTimeFromCamera.py

LOG_DATE=$(date +%y%m%d-%H%M)
mkdir -p $PATH_FOTOBOX/log

while true; do
    python $PATH_FOTOBOX/fotobox.py &> $PATH_FOTOBOX/log/fotobox_$LOG_DATE.log
    RETURN=$?
    echo "Exit code: $RETURN" >> $PATH_FOTOBOX/log/fotobox_$LOG_DATE.log

    # Shutdown
    if [[ $RETURN -eq 12 ]]; then
        sudo shutdown -h now
    fi
done
