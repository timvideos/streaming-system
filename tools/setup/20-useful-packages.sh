#!/bin/bash -ex
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Install a bunch of packages which are generally useful (such as vim).
#

# Editors
sudo apt-get install -y vim vim-gnome

# Revision control systems
sudo apt-get install -y git-core subversion bzr

# System tools
sudo apt-get install -y htop bash-completion

