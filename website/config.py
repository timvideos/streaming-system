#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Module which setups our configuration environment.

**
Everything should import this module and run the setup function before
doing anything else, *including imports*!
**
"""

import sys
import os


paths = [
    'third_party.zip'
]


def sys_path_insert(ipath):
    """Insert a path into sys if it doesn't exist already."""
    if ipath not in sys.path:
        sys.path.insert(0, ipath)


def setup_django():
    """Setup the django settings."""
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    from google.appengine.dist import use_library
    use_library('django', '1.2')


def setup():
    """Setup our configuration environment."""

    # Add our extra modules to sys.path
    for ipath in paths:
        sys_path_insert(ipath)

    setup_django()


def lint_setup():
    """Setup called to make pylint work."""
    if not "APPENGINE_SDK" in os.environ:
        print "Please set $APPENGINE_SDK to the location of the appengine SDK."
        return 1

    print "APPENGINE_SDK at ", os.environ["APPENGINE_SDK"]
    sys_path_insert(os.environ["APPENGINE_SDK"])

    for ipath in paths[:-1]:
        sys_path_insert(ipath.replace('.zip', ''))

    setup_django()
