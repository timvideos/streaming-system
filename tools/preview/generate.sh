#! /bin/sh

GROUPS=mission ab cd ef gh america

for GROUP in $GROUPS; do 
        (
         cd \#pycon-$GROUP
	 mplayer -nocache -nosound -vo png -cache 512 -nosound -vo png http://$GROUP.extractor.timvideos.us:8081/loop.raw -frames 1
         convert -resize 300x217 00000001.png 00000001-small.png
         pngcrush 00000001-small.png
         mv 00000001-small.png latest.png
        )
done
