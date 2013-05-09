#!/bin/bash -xe
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Enable the multiverse package repositories.
#

sudo apt-get --assume-yes install python-software-properties

# this doesn't work on precise
# sudo apt-add-repository multiverse

# so use these lines:
sudo apt-add-repository \
    "http://archive.ubuntu.com/ubuntu precise multiverse"
sudo apt-add-repository \
    "http://archive.ubuntu.com/ubuntu precise-updates multiverse"
sudo apt-add-repository \
    "http://archive.ubuntu.com/ubuntu precise-backports multiverse"
sudo apt-add-repository \
    "http://archive.ubuntu.com/ubuntu precise-security multiverse"

