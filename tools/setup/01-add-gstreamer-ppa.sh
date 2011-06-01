#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Adds the gstreamer developer's PPA. We need the newest packages for a number
# of advanced features.
#

# Install the PPA.
if [ ! -e /etc/apt/sources.list.d/gstreamer-developers-ppa-lucid.list ]; then
  apt-add-repository ppa:gstreamer-developers/ppa
fi

# Pin the PPA's gstreamer packages.
if grep "gstreamer" /etc/apt/preferences; then
  echo "gstreamer pinned."
else
  # Create a sources.d like directory.
  if [ ! -d /etc/apt/preferences.d ]; then
    mkdir /etc/apt/preferences.d
  fi

  # Put our pin there.
  cat >> /etc/apt/preferences.d/gstreamer-developers-ppa-lucid <<EOF
Explanation: Give the gstreamer PPA higher priority than anything else
Package: *
Pin: release o=LP-PPA-gstreamer-developers
Pin-Priority: 2000
EOF

  # Put our pin onto the end of the real preferences file.
  cat /etc/apt/preferences.d/gstreamer-developers-ppa-lucid \
    >> /etc/apt/preferences
fi
