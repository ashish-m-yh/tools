#!/bin/bash

SYNC_DIR=$1
SYNC_TO=$2

for i in `find $SYNC_DIR -type f`
do
        echo $i
        dest=`echo $i | sed -e "s#$SYNC_DIR##"`
        echo $dest
        rsync -W -ravP $i $SYNC_TO$dest &
        echo done with echo $?
done
