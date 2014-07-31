#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import cStringIO as StringIO
import os
import re
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


def _remove_comments(filename):
    fi = open(filename)

    fo = StringIO.StringIO()
    for line in fi.readlines():
        if re.match("^\s*//", line):
            continue
        if not line.strip():
            continue
        fo.write(line)

    fo.seek(0)
    return fo


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
        config = json.load(_remove_comments(public_config))
    except ValueError, e:
        raise IOError('Unable to open config.json\n%s' % e)

    if os.path.exists(private_config):
        try:
            config_private = json.load(_remove_comments(private_config))
        except Exception, e:
            raise IOError('Unable to open config.private.json\n%s' % e)
    else:
        warnings.warn('No config.private.json file!\n')
        config_private = {}

    _clean_empty(config)
    _clean_empty(config_private)

    _config_merge_into(config, config_private)

    all_keys = set(config['default'].keys())
    for group_name, group_config in config.iteritems():
        if group_name == "config":
            continue
        group_keys = set(group_config.keys())
        assert group_keys.issubset(all_keys), \
            'Group %s has invalid keys: %s' % (
                group_name, group_keys.difference(all_keys))

    return ConfigWrapper(config)


class ConfigWrapper(dict):

    def groups(self):
        """Get a list of groups defined in the config file."""
        groups = self.keys()
        groups.remove('config')
        groups.remove('default')
        groups.remove('example')
        return list(sorted(groups))

    def config(self, group):
        """Get a dictionary containing configuration values for a group."""
        assert group in self, "%s not %s" % (group, self.keys())
        config_group = {'group': group}
        for name, default_value in self['default'].iteritems():
            config_group[name] = self[group].get(name, default_value)

        for name, value in config_group.iteritems():
            context = dict(config_group)
            try:
                config_group[name] = value % context
            except:
                pass

        return config_group

    def valid(self, group):
        """Check if a given group is valid."""
        return group in self.groups()


def main(args):
    if args[-1] == 'groups':
        CONFIG = config_load()
        for group in CONFIG.groups():
            print group
        return 0

    # Check the json files
    print "config.json"
    print "="*80
    if os.system("cat config.json | grep -v '^\s*//' | python -m simplejson.tool") != 0:
        return -1
    print "="*80
    print
    print "config.private.json"
    print "="*80
    if os.system("cat config.private.json | grep -v '^\s*//' | python -m simplejson.tool") != 0:
        return -1
    print "="*80
    print

    # Try loading the config
    print "Loading config"
    CONFIG = config_load()
    print

    # Pretty print the resulting merged config output
    print "Merged config"
    print "="*80
    import pprint
    pprint.pprint(CONFIG)
    print "="*80

    # Print out each individual group
    for group in CONFIG.groups():
        print
        print group
        print "-"*80
        pprint.pprint(CONFIG.config(group))
        print "-"*80

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
