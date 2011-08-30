#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Updates the machine to the latest version of every installed package.
#

rm /etc/apt/apt.conf.d/02cache

# Remove any duplicate .save files which end up in /etc/apt/sources.list.d from
# installing PPAs multiple times. This prevents warning about duplicate sources.
rm /etc/apt/sources.list.d/*.save

# Update the software
aptitude update
aptitude full-upgrade -y
