#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Install a bunch of packages which are generally useful (such as vim).
#

# Editors
apt-get install -y vim vim-gnome

# Revision control systems
apt-get install -y git-core subversion bzr

# Useful python stuff
apt-get install -y python-setuptools python-software-properties

# System tools
apt-get install -y htop bash-completion
