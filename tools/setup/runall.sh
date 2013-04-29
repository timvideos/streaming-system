#!/bin/bash -x

# curl https://raw.github.com/CarlFK/streaming-system/master/tools/setup/runall.sh | bash
# curl https://raw.github.com/timvideos/streaming-system/master/tools/setup/runall.sh | bash

sudo apt-get install -y git-core

git clone https://github.com/CarlFK/streaming-system.git

streaming-system/tools/setup/00-get-timsvideo.sh

cd streaming-system/tools/setup

./01-add-multiverse.sh
./01-add-streamtime-ppa.sh
./05-update.sh
./20-gstreamer-packages.sh
./20-useful-packages.sh
./30-custom-flumotion.sh
./99-remove-ppa.sh

