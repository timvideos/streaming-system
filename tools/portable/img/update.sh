#! /bin/sh

for i in orig/*.png; do echo convert -resize 200x200 $i `basename $i`; done
