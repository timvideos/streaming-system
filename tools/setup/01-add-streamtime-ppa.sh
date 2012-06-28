#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Adds the gstreamer developer's PPA. We need the newest packages for a number
# of advanced features.
#

exit 0

# Install the PPA.
if [ ! -e /etc/apt/sources.list.d/gstreamer-developers-ppa-lucid.list ]; then
  apt-add-repository ppa:mithro/streamtime/ppa
fi

# Pin the PPA's gstreamer packages.
if grep "streamtime" /etc/apt/preferences; then
  echo "Our gstreamer repository pinned."
else
  # Create a sources.d like directory.
  if [ ! -d /etc/apt/preferences.d ]; then
    mkdir /etc/apt/preferences.d
  fi

  # Put our pin there.
  cat > /etc/apt/preferences.d/gstreamer-streamtime-ppa-lucid <<EOF
Explanation: Give the streamtime PPA higher priority than anything else
Package: *
Pin: release o=LP-PPA-streamtime
Pin-Priority: 2000
EOF

  # Put our pin onto the end of the real preferences file.
  cat /etc/apt/preferences.d/* > /etc/apt/preferences
fi
