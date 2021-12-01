#!/bin/bash

QUAYDIR=${QUAYDIR:-"/"}
QUAYPATH=${QUAYPATH:-"."}
QUAYCONF=${QUAYCONF:-"$QUAYPATH/conf"}
QUAYRUN=${QUAYRUN:-"$QUAYPATH/conf"}

QUAYENTRY=${QUAYENTRY:=$1}
QUAYENTRY=${QUAYENTRY:=registry}

cd $QUAYDIR
python $QUAYCONF/init/supervisord_conf_create.py $QUAYENTRY
