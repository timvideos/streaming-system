#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Enable the multiverse package repositories.
#

sudo apt-add-repository multiverse
exit

if grep -R multiverse /etc/apt/sources.list*; then
  echo "Multiverse already enabled."
else
  cat /etc/apt/sources.list | grep 'universe' | sed -e's/universe/multiverse/' > /tmp/multiverse.list
  mv /tmp/multiverse.list /etc/apt/sources.list.d/multiverse.list
fi
