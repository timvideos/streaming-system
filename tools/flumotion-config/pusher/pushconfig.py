#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Push config to a bunch of flumotion box."""

import optparse
import subprocess

config_path = os.path.realpath(os.path.dirname(__file__)+"/../../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()



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
    user = CONFIG['config']['user']
    password = CONFIG['config']['password']
    crypt = CONFIG['config']['crypt']
    rooms = common_config.groups(CONFIG)

    (options, args) = OPTIONS.parse_args()

    worker_context = dict(CONFIG['config'])
    #worker_context['flumotion-encoders'] = worker_context['flumotion-encoders'] % CONFIG

    # Write the worker
    worker_file = '/tmp/worker.xml'
    f = file(worker_file, 'w')
    f.write(file('worker.xml').read() % CONFIG['config'])
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
