#!/usr/bin/python
#
# libwebks.py - A set of library calls to interface to configs files
#
# Copyright 2008 NC State University
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

import webKickstart
import webKickstart.generator

class LibWebKickstart(object):

    def __init__(self, configDir='/etc/webkickstart'):
        self.configDir = configDir

    def getKeys(self, fqdn):
        """Returns a dict of TemplateVars or None if host is not defined."""

        wks = webKickstart.webKickstart("fakeurl", {}, self.configDir)
        mcList = wks.findFile(self.client, wks.config.hosts)
        
        if len(mcList) == 0:
            return None

        mc = mcList[0]
        try:
            # Debug mode is True to avoid special stuff...we just
            # want to query the config file
            g = webKickstart.generator.Gennerator(mc.getVersion(), mc, True)
        except Exception, e:
            # KeyError or ConfgError from webkickstart
            # Unsupported version key in config file
            g = webKickstart.generator.Gennerator('default', mc, True)

        g.runPlugins()
        return g.variables

    def getKey(self, fqdn, key):
        """Returns a list of strings for each instance of key defined for
           the specificed FQDN."""

        dict = self.getKeys(fqdn)
        if dict is None or not dict.has_key(key):
            return None

        return [ e.verbatim() for e in dict[key] ]

