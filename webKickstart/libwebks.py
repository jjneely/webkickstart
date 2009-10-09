#!/usr/bin/python
#
# libwebks.py - A set of library calls to interface to configs files
#
# Copyright 2008 - 2009 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
#
# SDG
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software

import logging
import webKickstart
import webKickstart.generator
import webKickstart.configtools

try:
    import hashlib
except ImportError:
    hashlib = None
    import sha

log = logging.getLogger('webks')

class LibWebKickstart(object):

    def __init__(self, configDir='/etc/webkickstart'):
        self.configDir = configDir

    def getGenerator(self, fqdn):
        """Returns a dict of TemplateVars or None if host is not defined."""

        wks = webKickstart.webKickstart("fakeurl", {}, self.configDir)
        mcList = wks.findMC(fqdn)
        
        if len(mcList) == 0:
            log.debug("LibWebKickstart: Did not find config: %s" % fqdn)
            return None

        mc = mcList[0]
        if mc.isKickstart(): 
            log.debug("LibWebKickstart: %s has a pre-defined kickstart." % fqdn)
            return None

        try:
            # Debug mode is True to avoid special stuff...we just
            # want to query the config file
            g = webKickstart.generator.Generator(mc.getVersion(), mc, True)
        except Exception, e:
            # KeyError or ConfgError from webkickstart
            # Unsupported version key in config file
            log.warning("Building a default config for %s which may fail." % fqdn)
            g = webKickstart.generator.Generator('default', mc, True)

        g.localVars(fqdn)
        g.buildPostVar()
        g.runPlugins()
        return g

    def getHash(self, files):
        """Return a unique hash of the webkickstart source config files.
           This can be used to detect changes.  The files argument is a list
           of webkickstart source config files."""

        if hashlib is not None:
            sha = hashlib.sha1()
        else:
            sha = sha.new()

        for file in files:
            try:
                fd = open(file)
                sha.update(fd.read())  # small files right?
                fd.close()
            except IOError:
                continue

        return sha.hexdigest()

    def getEverything(self, fqdn):
        """Returns a dict of all keys, scripts, and files included in a 
           webkickstart.  Intended for interaction with a database."""

        # Pull all the keys from parsing the clients web-kickstart
        # Transmute it into something we can store in the database
        # Remeber all the file names that make up the web-kickstart so
        #   we can see if we need to do this again later

        genny = self.getGenerator(fqdn)
        keys = genny.variables
        dbsafe = {}

        def rHelper(prefix, keys, dbsafe):
            for key in keys.keys():
                if key in ['webKickstart', 'WebKickstartError', 'ParseError']:
                    # Exception classes and meta info passed 
                    # to webks genshi templates
                    continue
                dbsafe[prefix+key] = keys[key].table
                if len(keys[key].members) > 0:
                    rHelper("%s%s." % (prefix, key), keys[key].members, dbsafe)

        rHelper("", keys, dbsafe)

        dbsafe['webKickstart.scripts'] = \
                [ t[0] for t in keys['webKickstart'].scripts.table ]

        dbsafe['webKickstart.files'] = \
                [ m[1].getFileName() for m in genny.configs ]

        dbsafe['webKickstart.hash'] = \
                self.getHash(dbsafe['webKickstart.files'])

        return dbsafe

    def getKeys(self, fqdn):
        """Returns a dict of TemplateVars or None if host is not defined."""

        g = self.getGenerator(fqdn)
        if g is None:
            return {}
        else:
            return g.variables

    def getKey(self, fqdn, key):
        """Returns a list of strings for each instance of key defined for
           the specificed FQDN."""

        dict = self.getKeys(fqdn)
        if dict is None or not dict.has_key(key):
            return None

        return [ e.verbatim() for e in dict[key] ]

    def getProfileKeys(self, fqdn):
        g = self.getGenerator(fqdn)
        cfg = webKickstart.configtools.config

        if cfg is None:
            log.debug("WebKickstart configuration not setup??")
            return None

        return cfg.getProfileVars(g.profile)

