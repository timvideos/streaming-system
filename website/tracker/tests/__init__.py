#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import os
from django_testing_fixes.suite import create_suite

suite = create_suite(os.path.split(os.path.dirname(__file__))[0], "tracker")
