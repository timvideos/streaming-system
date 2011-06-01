#!/bin/bash
#
# Copyright 2011 Google Inc. All Rights Reserved.
# Author: tansell@google.com (Tim Ansell)
#
# Install the gstreamer packages needed by our flumotion setup.
#
apt-cache policy gstreamer-tools
apt-get install -y gstreamer0.10.* python-gst0.10 gstreamer-tools
