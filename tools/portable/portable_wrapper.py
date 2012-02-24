#!/usr/bin/python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4
#
# Flumotion - a streaming media server
# Copyright (C) 2004,2005,2006 Fluendo, S.L. (www.fluendo.com).
# All rights reserved.

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE.GPL" in the source distribution for more information.

# Licensees having purchased or holding a valid Flumotion Advanced
# Streaming Server license may use this file in accordance with the
# Flumotion Advanced Streaming Server Commercial License Agreement.
# See "LICENSE.Flumotion" in the source distribution for more information.

# Headers in this file shall remain intact.

import os
import sys

# Variable templates
LIBDIR = '/usr/local/lib'
PROGRAM_PATH = 'portable.main'

os.chdir(os.path.dirname(__file__))

try:
    # setup the project root
    dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(dir, '..', 'flumotion', '.svn')) or \
       os.path.exists(os.path.join(dir, '..', '.git')):
        root = os.path.split(dir)[0]
    else:
        root = os.path.join(LIBDIR, 'flumotion', 'python')
    sys.path.insert(0, root)

    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)

    # and boot!
    from flumotion.common import boot
    boot.boot(PROGRAM_PATH, gtk=True, gst=True, installReactor=True)

except KeyboardInterrupt:
    print 'Interrupted'
