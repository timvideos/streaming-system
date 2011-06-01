#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)

# Install the required vlc packages.
apt-get install -y vlc.*

# Get the jtvlc package.
if [ ! -e jtvlc ]; then
  git clone git://github.com/justintv/jtvlc.git
else
  (
    cd jtvlc
    git update
  )
fi
