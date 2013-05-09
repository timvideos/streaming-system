#!/bin/bash -ex
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Install the gstreamer packages needed by our flumotion setup.
#

# make sure your getting the gstreamer-tools from where you think you are
# apt-cache policy gstreamer-tools

sudo apt-get install -y gstreamer0.10.* python-gst0.10 gstreamer-tools
