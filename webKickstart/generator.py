#!/usr/bin/python
#
# generator.py - Build kickstarts from MetaConfigs
#
# Copyright 2008 NC State University
# Written by Jack Neely <jjneely@pams.ncsu.edu>
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

import configtools

from metaparser import MetaParser
from errors import *

log = logging.getLogger("webks")

class Generator(object):

    def __init__(self, profile, mc=None):
        self.profile = profile
        self.configs = []
        self.variables = []          # an ordered list - the order we found
                                     # the keys in

        if mc != None:
            self.includeFile(mc)
            self.configs.append(mc)
            self.__handleIncludes(mc, configtools.include_key)

    def makeKS(self):
        # return a string of a Red Hat Kickstart
        return ""

    def __handleIncludes(self, mc, key):
        """Handle recursive includes"""

        for rec in mc.parseCommands():
            if rec[0] == key:
                if len(rec) <= 1:
                    msg = "'%s' key must have one argument." % key
                    raise errors.ParseError, msg
                else:
                    tmp_mc = MetaConfig(rec[1])
                    self.includeFile(tmp_mc)
                    self.__handleIncludes(tmp_mc, key)


    def includeFile(self, mc):
        """Parse a solarisConfig object."""
        
        if mc in self.configs:
            msg = "Recursive '%s' loop detected." % configtools.include_key
            raise errors.ParseError, msg

        for rec in t:
            self.table.append(rec)

        self.configs.append(mc)
        
