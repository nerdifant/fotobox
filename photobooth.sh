#!/bin/bash

PHOTOBOOTH_DIR=/home/pi/git/photobooth

cd "${PHOTOBOOTH_DIR}"

if [[ $1 == "set-time" ]]; then
  python set-time.py
fi

python photobooth.py >>photobooth.log 2>>photobooth.err

cd -

