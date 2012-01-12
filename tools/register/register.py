#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Connect to the streamti.me server and report our stats."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"

import time
import urllib2

from flumotion.common import errors, planet, log
from flumotion.monitor.nagios import util
from flumotion.common.planet import moods

from flumotion.admin.command import common

from flumotion.admin.command import main


class Reporter(command.AdminCommand):

    def _callback(self, result):
        d = self.getRootCommand().medium.callRemote('getPlanetState')

        def gotPlanetStateCb(planetState):
            workers = planetState.get('workers')
            for f in planetState.get('flows'):
                for component in f.get('components'):
                    if not component.get('name').startswith('http'):
                        continue

                    def getUIStateCb(uiState):
                        self.clients += uiState.get('clients-current')
                        self.bitrate += uiState.get('bitrate-current')

                    d = self.medium.componentCallRemote(
                        componentCommand.componentState, 'getUIState')
                    d.addCallback(getUIStateCb)
                    yield d

        d.addCallback(gotPlanetStateCb)
        return d


class Command(main.Command):
    description = "Send stats to the streamti.me server."

    subCommandClasses = [Register]



def main(argv):
  myip = urllib2.urlopen('http://whatismyip.org').read().strip()
  print 'My IP address is:', repr(myip)

  while True:
    clients = 0
    for http_object in c

    bitrate = 0


    urllib2.urlopen('http://view.streamti.me/register', {
        'group': argv[0],
        'ip': myip,
        'clients': clients,
        'bitrate': bitrate,
        }).read().strip()


if __name__ == '__main__':
  import sys
  main(sys.argv)
