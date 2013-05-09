#!/bin/bash -ex
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Install our custom version of flumotion.
#

# this script should be next to flumotion and flumotion-ugly

set -x
set -e

# Make sure a local flumotion isn't install
sudo apt-get remove flumotion || true

# Dependencies to build stuff
sudo apt-get install --assume-yes build-essential autoconf autopoint libtool libxml-parser-perl python-dev libvorbis-dev libogg-dev libtheora-dev libvpx-dev subversion

# FIXME(mithro): Temporary hack for lca's natty boxes
# apt-get install --assume-yes autopoint || true
# apt-get install --assume-yes gstreamer0.10-plugins-.*-multiverse gstreamer0.10-ffmpeg || true
# FIXME(mithro): End

# Dependencies to run flumotion
sudo apt-get install --assume-yes python-kiwi python-twisted.* ssl-cert

# Install the core flumotion
(
  cd ../flumotion
  git clean -f -x
  ./autogen.sh
  make -j16
  sudo make install
)

# Install the ugly plugins
(
  cd ../flumotion-ugly
  git clean -f -x
  ./autogen.sh
  make -j16
  sudo make install
)

# Add a flumotion user
if grep flumotion /etc/passwd; then
  echo "Flumotion user already created."
else
  sudo adduser --system --quiet --home /usr/local/var/run/flumotion \
    --shell /usr/sbin/nologin --no-create-home --group \
    --disabled-password --disabled-login \
    --gecos "Flumotion Streaming Server" flumotion
fi

# Copy the config files to /etc
sudo cp -rf ../flumotion-config/fromdeb/etc/* /usr/local/etc/
sudo ln -sf /usr/local/etc/init.d/flumotion /etc/init.d/flumotion

# Create a SSL certificate used for encryption.
sudo make-ssl-cert /usr/share/ssl-cert/ssleay.cnf /usr/local/etc/flumotion/default.pem || true
sudo chown flumotion:flumotion /usr/local/etc/flumotion/default.pem

# Give access to the firewire ports
sudo adduser flumotion video
