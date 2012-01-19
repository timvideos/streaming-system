#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Push config to a bunch of flumotion box."""

import ConfigParser
import optparse
import subprocess


CONFIG = ConfigParser.ConfigParser()
CONFIG.read(['config.ini'])

OPTIONS = optparse.OptionParser()
OPTIONS.add_option("-e", "--encoders",
                  action="store_true", dest="encoders", default=True,
                  help="Push configs to encoders.")
OPTIONS.add_option("--no-encoders",
                  action="store_false", dest="encoders",
                  help="Don't push configs to encoders.")
OPTIONS.add_option("-c", "--collectors",
                  action="store_true", dest="collectors", default=True,
                  help="Push configs to collectors.")
OPTIONS.add_option("--no-collectors",
                  action="store_false", dest="collectors",
                  help="Don't push configs to collectors.")

def main(args):
    user = CONFIG.get('config', 'user')
    password = CONFIG.get('config', 'password')
    crypt = CONFIG.get('config', 'crypt')
    rooms = CONFIG.get('config', 'rooms').split()

    (options, args) = OPTIONS.parse_args()

    # Write the worker
    worker_file = '/tmp/worker.xml'
    f = file(worker_file, 'w')
    f.write(file('worker.xml').read() % locals())
    f.close()

    for room in rooms:
        justintv = CONFIG.get('justintv', room)

        print room
        print "-"*80

        # Upload the encoder config
        if options.encoders:
            host = CONFIG.get('encoders', room)

            encoder_file = '/tmp/encoder-lca-%s.xml' % room
            f = file(encoder_file, 'w')
            f.write(file('encoder-lca.xml').read() % locals())
            f.close()

            print "Encoder - %s" % host
            subprocess.call("scp %s %s:/usr/local/etc/flumotion/managers/default/planet.xml" % (encoder_file, host), shell=True)
            subprocess.call("scp %s %s:/usr/local/etc/flumotion/workers/default.xml" % (worker_file, host), shell=True)

        # Upload the collector config
        if options.collectors:
            host = CONFIG.get('collectors', room)

            collector_file = '/tmp/collector-lca-%s.xml' % room
            f = file(collector_file, 'w')
            f.write(file('collector-lca.xml').read() % locals())
            f.close()

            print "Collector - %s" % host
            subprocess.call("scp %s %s:/usr/local/etc/flumotion/managers/default/planet.xml" % (collector_file, host), shell=True)
            subprocess.call("scp %s %s:/usr/local/etc/flumotion/workers/default.xml" % (worker_file, host), shell=True)

        print "-"*80
        print

if __name__ == "__main__":
    import sys
    main(sys.argv)
