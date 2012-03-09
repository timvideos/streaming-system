#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Push config to a bunch of flumotion box."""

import crypt
import optparse
import os
import subprocess
import sys

mypath = os.path.dirname(__file__)
if not mypath:
    mypath = "."

config_path = os.path.realpath(mypath+"/../../..")
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
    (options, args) = OPTIONS.parse_args()

    general_context = dict(CONFIG['config'])

    # Write the worker

    for group in CONFIG.groups():
        config = CONFIG.config(group)
        config['flumotion-password-crypt'] = crypt.crypt(
            config['flumotion-password'],
            config['flumotion-salt'])
        config['group'] = group

        print group
        print "-"*80

        worker_file = '/tmp/worker-%s.xml' % group
        f = file(worker_file, 'w')
        f.write(file('worker.xml').read() % config)
        f.close()

        # Upload the encoder config
        if options.encoders:
            host = config['flumotion-encoder']

            encoder_file = '/tmp/encoder-%s.xml' % group
            f = file(encoder_file, 'w')
            f.write(file('encoder.xml').read() % config)
            f.close()

            print "Encoder - %s" % host
            subprocess.call("echo scp %s root@%s:/usr/local/etc/flumotion/managers/default/planet.xml" % (encoder_file, host), shell=True)
            subprocess.call("echo scp %s root@%s:/usr/local/etc/flumotion/workers/default.xml" % (worker_file, host), shell=True)

        # Upload the collector config
        if options.collectors:
            host = config['flumotion-collector']

            collector_file = '/tmp/collector-%s.xml' % group
            f = file(collector_file, 'w')
            f.write(file('collector.xml').read() % config)
            f.close()

            print "Collector - %s" % host
            subprocess.call("echo scp %s root@%s:/usr/local/etc/flumotion/managers/default/planet.xml" % (collector_file, host), shell=True)
            subprocess.call("echo scp %s root@%s:/usr/local/etc/flumotion/workers/default.xml" % (worker_file, host), shell=True)

        print "-"*80
        print

if __name__ == "__main__":
    import sys
    main(sys.argv)
