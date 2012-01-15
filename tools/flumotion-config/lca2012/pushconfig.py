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
	# Upload the encoder config
	encoder_file = '/tmp/encoder-lca-%s.xml' % room
	f = file(encoder_file, 'w')
	f.write(file('encoder-lca.xml').read() % locals())
	f.close()

	#subprocess.call("scp %s %s:/usr/local/etc/flumotion/managers/default/planet.xml" % (encoder_file, room))
	#subprocess.call("scp %s %s:/usr/local/etc/flumotion/workers/default.xml" % (worker_file, room))

	# Upload the collector config
	collector_file = '/tmp/collector-lca-%s.xml' % room
	config = file('collector-lca.xml').read() % locals()
	f = file(collector_file, 'w')
	f.write(config)
	f.close()

	#subprocess.call("scp %s root@%s.front.lca:/usr/local/etc/flumotion/managers/default/planet.xml" % (encoder_file, room))
	#subprocess.call("scp %s root@%s.front.lca:/usr/local/etc/flumotion/workers/default.xml" % (worker_file, room))
