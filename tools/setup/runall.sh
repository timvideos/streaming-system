#!/bin/bash -x

# wget -N https://raw.github.com/timvideos/streaming-system/master/tools/setup/runall.sh
# chmod u+x runall.sh
# ./runall.sh

sudo apt-get install -y git-core

git clone https://github.com/CarlFK/streaming-system.git

cd streaming-system/tools/setup

00-get-timsvideo.sh
01-add-multiverse.sh
01-add-streamtime-ppa.sh
05-update.sh
20-gstreamer-packages.sh
20-useful-packages.sh
30-custom-flumotion.sh
99-remove-ppa.sh
