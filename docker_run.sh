#!/bin/bash

DIR=`dirname "$(readlink -f "$0")"`
docker build -t governor $DIR
docker run -v $DIR:/governor -it governor python3 /governor/src/main.py
