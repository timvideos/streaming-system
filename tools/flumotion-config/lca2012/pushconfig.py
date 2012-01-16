#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Push config to a bunch of flumotion box."""

import ConfigParser
import subprocess

config = ConfigParser.ConfigParser()
config.read(['config.ini'])

user = config.get('config', 'user')
password = config.get('config', 'password')
crypt = config.get('config', 'crypt')
rooms = config.get('config', 'rooms').split()

# Write the worker
worker_file = '/tmp/worker.xml'
f = file(worker_file, 'w')
f.write(file('worker.xml').read() % locals())
f.close()

for room in rooms:
    print room
    print "-"*80
    # Upload the encoder config
    encoder_file = '/tmp/encoder-lca-%s.xml' % room
    f = file(encoder_file, 'w')
    f.write(file('encoder-lca.xml').read() % locals())
    f.close()

    print "Encoder"
    subprocess.call("scp %s %s:/usr/local/etc/flumotion/managers/default/planet.xml" % (encoder_file, room), shell=True)
    subprocess.call("scp %s %s:/usr/local/etc/flumotion/workers/default.xml" % (worker_file, room), shell=True)

    # Upload the collector config
    collector_file = '/tmp/collector-lca-%s.xml' % room
    config = file('collector-lca.xml').read() % locals()
    f = file(collector_file, 'w')
    f.write(config)
    f.close()

    print "Collector"
    subprocess.call("scp %s root@front.%s.lca:/usr/local/etc/flumotion/managers/default/planet.xml" % (collector_file, room), shell=True)
    subprocess.call("scp %s root@front.%s.lca:/usr/local/etc/flumotion/workers/default.xml" % (worker_file, room), shell=True)
    print "-"*80
    print
