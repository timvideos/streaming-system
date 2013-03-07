#! /bin/bash

if [ `whoami` != "irc" ]; then
  exec sudo su irc -c "/home/irc/logs/updatelogs.sh"
fi

i="0"
while [ $i -lt 4 ]; do
  for logdir in /home/irc/logs/ChannelLogger/freenode/*; do
    if [ -d $logdir ]; then
      logs2html $logdir
      /home/irc/logs/latest2preview.py $logdir/latest.log.html > $logdir/preview.log.html
    fi
  done
  sleep 1
  i=$(( $i + 1 ))
done
date
sleep 5
exec /home/irc/logs/updatelogs.sh
