#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Adds the VLC developer's PPA. We need the latest vlc so we can stream to
# justin.tv
#

# Install the PPA.
if [ ! -e /etc/apt/sources.list.d/lucid-bleed-ppa-lucid.list ]; then
  add-apt-repository ppa:lucid-bleed/ppa
fi

# Pin the PPA's gstreamer packages.
if grep "lucid-bleed" /etc/apt/preferences; then
  echo "vlc pinned."
else
  # Create a sources.d like directory.
  if [ ! -d /etc/apt/preferences.d ]; then
    mkdir /etc/apt/preferences.d
  fi

  # Put our pin there.
    cat >> /etc/apt/preferences.d/lucid-bleed-ppa-lucid <<EOF
Explanation: Give the vlc PPA higher priority than anything else
Package: *
Pin: release o=LP-PPA-lucid-bleed
Pin-Priority: 2000
EOF

  # Put our pin onto the end of the real preferences file.
  cat /etc/apt/preferences.d/lucid-bleed-ppa-lucid \
    >> /etc/apt/preferences
fi
