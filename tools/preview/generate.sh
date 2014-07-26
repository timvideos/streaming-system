#! /bin/bash

trap "kill 0" SIGINT SIGTERM EXIT

CHANNELS="$(python ../../config.py groups)"

for CHANNEL in $CHANNELS; do
        mkdir /srv/$CHANNEL
done

for CHANNEL in $CHANNELS; do
        cd /srv
        if ping $CHANNEL.encoder.timvideos.us -c 1 -W 1; then
               echo "$CHANNEL up"
        else
               echo "$CHANNEL down, skipping"
               continue
        fi
        while true; do
                (
                 cd $CHANNEL
                 echo "$CHANNEL Getting image..."
                 mplayer -nocache -nosound -vo png -cache 512 -nosound -vo png http://$CHANNEL.encoder.timvideos.us:8081/loop.raw -frames 1 >/dev/null 2>&1
                 echo "$CHANNEL resizing..."
                 convert -resize 300x217 00000001.png 00000001-small.png >/dev/null 2>&1
                 echo "$CHANNEL crushing..."
                 pngcrush 00000001-small.png 00000001-crush.png >/dev/null 2>&1
                 echo "$CHANNEL moving..."
                 mv 00000001-crush.png latest.png >/dev/null 2>&1
                 echo
                )
                sleep 1
        done &
done
wait
