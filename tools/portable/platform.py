#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import subprocess

def get_power_status():
    """Returns true if the laptop is on AC."""
    p = subprocess.Popen('acpi -V', shell=True, stdout=subprocess.PIPE)

    try:
        for line in p.stdout.readlines():
            if line.startswith('Adapter'):
                return line.split(': ')[-1].strip() == "on-line"

        return False
    finally:
        p.communicate(None)
        assert p.returncode == 0

def get_network_status():
    """Returns true if the laptop is connected to the Telstra AP."""
    p = subprocess.Popen('nm-tool', shell=True, stdout=subprocess.PIPE)
    (stdout, stderr) = p.communicate(None)

    devices = stdout.split('- Device: ')

    # FIXME(tansell): Check the actual nm devices to make sure it's the wifi
    # connected and it's connected to the telstra device.
    return "State: connected" in devices[0]


if __name__ == "__main__":
    print "Power:", get_power_status()
    print "Network:", get_network_status()

