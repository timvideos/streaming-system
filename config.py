#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import os
import simplejson as json
import warnings

def _config_merge_into(dicta, dictb):
    for nameb, valueb in dictb.iteritems():
        if nameb in dicta and isinstance(dicta[nameb], dict):
            valuea = dicta[nameb]
            assert isinstance(valuea, dict), "%r not dict" % valuea
            assert isinstance(valueb, dict), "%r not dict" % valueb

            _config_merge_into(valuea, valueb)
        else:
            dicta[nameb] = valueb


def _skip_start_comments(f):
    while True:
        value = f.read(2)
        if value == '//':
            f.readline()
            continue
        break
    f.seek(-2, os.SEEK_CUR)
    return f


def _clean_empty(dicta):
    if "" in dicta:
        del dicta[""]

    for name, value in dicta.items():
        if isinstance(value, dict):
            _clean_empty(value)


def config_load():
    """Load configuration and return dictionary."""
    myloc = os.path.dirname(__file__)
    if not myloc:
        myloc = "."
    public_config = myloc+'/config.json'
    private_config = myloc+'/config.private.json'

    try:
        config = json.load(_skip_start_comments(open(public_config)))
    except ValueError, e:
        raise IOError('Unable to open config.json\n%s' % e)
    try:
        config_private = json.load(_skip_start_comments(open(private_config)))
    except (ValueError, IOError), e:
        warnings.warn('Unable to open config.private.json\n%s' % e)
        config_private = {}

    _clean_empty(config)
    _clean_empty(config_private)

    _config_merge_into(config, config_private)

    all_keys = set(config['default'].keys())
    for channel_name, channel_config in config.iteritems():
        if channel_name == "config":
            continue
        channel_keys = set(channel_config.keys())
        assert channel_keys.issubset(all_keys), \
            'Group %s has invalid keys: %s' % (
                channel_name, channel_keys.difference(all_keys))

    return ConfigWrapper(config)


class ConfigWrapper(dict):

    def channels(self):
        """Get a list of channels defined in the config file."""
        channels = self.keys()
        channels.remove('config')
        channels.remove('default')
        return list(sorted(channels))

    def config(self, channel):
        """Get a dictionary containing configuration values for a channel."""
        assert channel in self, "%s not %s" % (channel, self.keys())
        config_channel = {'channel': channel}
        for name, default_value in self['default'].iteritems():
            config_channel[name] = self[channel].get(name, default_value)

        for name, value in config_channel.iteritems():
            context = dict(config_channel)
            try:
                config_channel[name] = value % context
            except:
                pass

        return config_channel

    def valid(self, channel):
        """Check if a given channel is valid."""
        return channel in self.channels()


if __name__ == "__main__":
    print "config.json"
    print "-"*80
    os.system("cat config.json | grep -v '^//' | python -m simplejson.tool")
    print "-"*80
    print
    print "config.private.json"
    print "-"*80
    os.system("cat config.private.json | grep -v '^//' | python -m simplejson.tool")
    print "-"*80
    print
    print "Merged config"
    print "-"*80
    CONFIG = config_load()
    import pprint
    pprint.pprint(CONFIG)
    print "-"*80
    for channel in CONFIG.channels():
        print channel
        pprint.pprint(CONFIG.config(channel))

