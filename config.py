#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import os
import simplejson as json
import warnings

def _config_merge_into(dicta, dictb):
    for nameb, valueb in dictb.iteritems():
        if nameb == "":
            del dicta[nameb]
            continue

        if nameb in dicta:
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
        warnings.warn('Unable to open config_private.json\n%s' % e)
        config_private = {}

    _config_merge_into(config, config_private)

    all_keys = set(config['default'].keys())
    for group_name, group_config in config.iteritems():
        if group_name == "config":
            continue
        group_keys = set(group_config.keys())
        assert group_keys.issubset(all_keys), \
            'Group %s has invalid keys: %s' % (
                group_name, group_keys.difference(all_keys))

    return config


def config_all(config, group):
    """Get a dictionary containing configuration values."""
    assert group in config
    config_group = {}
    for name, default_value in config['default'].iteritems():
        config_group[name] = config[group].get(name, default_value)
    return config_group


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
    config = config_load()
    import pprint
    pprint.pprint(config)
    print "-"*80

