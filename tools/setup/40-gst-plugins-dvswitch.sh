#!/bin/bash -ex
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Install gst-plugins-dvswitch
#


set -x
set -e

# Dependencies to build stuff
sudo apt-get install --assume-yes build-essential autoconf autopoint libtool libxml-parser-perl python-dev libvorbis-dev libogg-dev libtheora-dev libvpx-dev subversion


# build and install
(
  cd 
  git clone https://github.com/timvideos/gst-plugins-dvswitch.git
  cd gst-plugins-dvswitch
  git clean -f -x
  ./autogen.sh
  make 
  sudo make install
)

sudo ln -s /usr/local/lib/gstreamer-0.10/libgstdvswitch.so /usr/lib/gstreamer-0.10/

