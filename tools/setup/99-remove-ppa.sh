#!/bin/bash -ex
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Clean up the things we added that cause problems for our system configuration
# system.
#

# Remove the ppa files as they cause problems for puppet.
rm /etc/apt/sources.list.d/*ppa*
