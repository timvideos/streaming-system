#! /usr/bin/python
# vim: set ts=4 sw=4 et sts=4 ai:

import os, sys
config_path = os.path.realpath(os.path.dirname(__file__)+"../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()

print
print
print

print """\
supybot.networks.freenode.channels: %s
""" % " ".join(CONFIG.config(group)['ircchannel'] for group in CONFIG.groups()),

print
print
print

print """\
# RSS Configuration
supybot.plugins.RSS.waitPeriod: 60
""",

for group in CONFIG.groups():
    print """\
supybot.plugins.RSS.announce.%s: %s
""" % (CONFIG.config(group)['ircchannel'], group),

print """\
supybot.plugins.RSS.feeds: %s
""" % " ".join(CONFIG.groups()),

for group in CONFIG.groups():
    print """\
supybot.plugins.RSS.feeds.%s: http://timvideos.us/%s/rss
""" % (group, group),



