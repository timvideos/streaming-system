#!/bin/bash -ex
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Updates the machine to the latest version of every installed package.
#

sudo rm /etc/apt/apt.conf.d/02cache || true

# Remove any duplicate .save files which end up in /etc/apt/sources.list.d from
# installing PPAs multiple times. This prevents warning about duplicate sources.
sudo rm /etc/apt/sources.list.d/*.save || true

# Update the software
sudo apt-get install aptitude
sudo aptitude update
sudo aptitude full-upgrade -y
