#!/bin/bash

source common.sh

# Copy the ffserver config up
FFSERVERCONF=/tmp/$SERVER.ffserver.conf
cat ffserver/ffserver.conf.$TYPE | sed -e"s/\$COLLECTOR/$COLLECTOR/" > $FFSERVERCONF
scp $FFSERVERCONF $USER@$SERVER:/tmp/ffserver.conf
$SUDO "mv /tmp/ffserver.conf /etc/ffserver.conf"
rm $FFSERVERCONF

# Start ffserver
$SUDO killall ffserver
$SUDO ffserver

# Ping the appengine app with our details...
$SUDO wget http://tims-video.appspot.com/$TYPE/register
