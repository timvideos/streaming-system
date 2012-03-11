#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Connect to the streamti.me server and report our stats."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"


class Counter(object):
    def __init__(self):
        self.count = 0

    def acquire(self, empty=False):
        if empty and self.count != 0:
            return False
        self.count += 1
        return True

    def release(self):
        self.count -= 1
