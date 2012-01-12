#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import cStringIO as StringIO

import subprocess
import unittest

import mox

import portable_platform


def subprocess_mock(mox, *args, **kw):
    mock_process = mox.CreateMock(subprocess.Popen)
    mox.StubOutWithMock(subprocess, 'Popen', use_mock_anything=True)

    subprocess.Popen(*args, **kw).AndReturn(
        mock_process)
    return mock_process


class ACStatusTest(mox.MoxTestBase):

    acpi_online = """\
Battery 0: Full, 100%
Battery 0: design capacity 6760 mAh, last full capacity 3355 mAh = 49%
Adapter 0: on-line
Thermal 0: ok, 49.0 degrees C
Thermal 0: trip point 0 switches to mode critical at temperature 104.0 degrees C
Thermal 0: trip point 1 switches to mode passive at temperature 91.5 degrees C
Thermal 1: ok, 51.0 degrees C
Thermal 1: trip point 0 switches to mode critical at temperature 127.0 degrees C
Cooling 0: LCD 0 of 15
Cooling 1: Processor 0 of 10
Cooling 2: Processor 0 of 10
"""

    acpi_offline = """\
Battery 0: Discharging, 99%, 02:13:26 remaining
Battery 0: design capacity 6844 mAh, last full capacity 3397 mAh = 49%
Adapter 0: off-line
Thermal 0: ok, 48.0 degrees C
Thermal 0: trip point 0 switches to mode critical at temperature 104.0 degrees C
Thermal 0: trip point 1 switches to mode passive at temperature 91.5 degrees C
Thermal 1: ok, 54.0 degrees C
Thermal 1: trip point 0 switches to mode critical at temperature 127.0 degrees C
Cooling 0: LCD 8 of 15
Cooling 1: Processor 0 of 10
Cooling 2: Processor 0 of 10
"""

    def test_offline(self):
        mock_process = subprocess_mock(self.mox, 'acpi -V', shell=True, stdout=subprocess.PIPE)
        mock_process.stdout = StringIO.StringIO(self.acpi_offline)
        mock_process.communicate(None).AndReturn(('', ''))
        mock_process.returncode = 0
        self.mox.ReplayAll()

        self.assertFalse(portable_platform.get_ac_status())

    def test_online(self):
        mock_process = subprocess_mock(self.mox, 'acpi -V', shell=True, stdout=subprocess.PIPE)
        mock_process.stdout = StringIO.StringIO(self.acpi_online)
        mock_process.communicate(None).AndReturn(('', ''))
        mock_process.returncode = 0
        self.mox.ReplayAll()

        self.assertTrue(portable_platform.get_ac_status())



if __name__ == '__main__':
  unittest.main()
