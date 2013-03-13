#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Install our custom version of flumotion.
#

set -x
set -e

# Make sure a local flumotion isn't install
apt-get remove flumotion || true

# Dependencies to build stuff
apt-get install -y build-essential autoconf libtool libxml-parser-perl python-dev libvorbis-dev libogg-dev libtheora-dev libvpx-dev subversion

# FIXME(mithro): Temporary hack for lca's natty boxes
apt-get install -y autopoint || true
apt-get install -y gstreamer0.10-plugins-.*-multiverse gstreamer0.10-ffmpeg || true
# FIXME(mithro): End

# Dependencies to run flumotion
apt-get install -y python-kiwi python-twisted.* ssl-cert

# Install the core flumotion
(
  cd timvideos/tools/flumotion
  git clean -f -x
  ./autogen.sh
  make -j16
  make install
)

# Install the ugly plugins
(
  cd timvideos/tools/flumotion-ugly
  git clean -f -x
  ./autogen.sh
  make -j16
  make install
)

# Add a flumotion user
if grep flumotion /etc/password; then
  echo "Flumotion user already created."
else
  adduser --system --quiet --home /usr/local/var/run/flumotion \
    --shell /usr/sbin/nologin --no-create-home --group \
    --disabled-password --disabled-login \
    --gecos "Flumotion Streaming Server" flumotion
fi

# Copy the config files to /etc
cp -rf timvideos/tools/flumotion-config/fromdeb/etc/* /usr/local/etc/
ln -sf /usr/local/etc/init.d/flumotion /etc/init.d/flumotion

# Create a SSL certificate used for encryption.
make-ssl-cert /usr/share/ssl-cert/ssleay.cnf /usr/local/etc/flumotion/default.pem || true
chown flumotion:flumotion /usr/local/etc/flumotion/default.pem

# Give access to the firewire ports
chmod a+rw /dev/raw1394 || true
