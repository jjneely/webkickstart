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

class TemplateVar(object):

    def __init__(self, tokens):
        if len(tokens) == 0:
            msg = "Invalid row read from metaconfig file."
            raise ParseError, msg

        self.tokens = tokens

    def verbatim(self):
        return ' '.join(self.tokens)

    def __str__(self):
        return self.verbatim()

    def __getitem__(self, idx):
        return self.tokens[idx]

    def __setitem__(self, idx, val):
        pass

    def key(self):
        return self.tokens[0]

    def options(self):
        return self.tokens[1:]

    def len(self):
        return len(self.tokens[1:])


class MetaTable(object):

    """This is the object that the Cheetah template will have to
       reference all the meta data from the metaconfig.  This needs to
       be very easy to use and be realtively syntax clean so we don't
       confuse folks with [[}(--): crap everywhere.

       Even though we support multiple instances of the same key in a
       metaconfig, we assume that for most cases the template author only
       really wants the top level one.  (The primary config file overriding
       the same key if found in include files lower down the include tree.)

       So MetaTable['foo'] will always return a single TemplateVar.  Use
       MetaTable.interate('foo') in a for loop to support multiple keys.
    """

    def __init__(self):
        self.data = {}

    def isDefined(self, key):
        return self.data.has_key(key)

    def getOptionLength(self, key):
        if self.isDefined(key):
            return len(self.data[key])
        else:
            return None

    def interate(self, key):
        if self.isDefined(key):
            return self.data[key]
        else:
            return []

    def __getitem__(self, key):
        return self.data[key][0]

    def __setitem__(self, key, value):
        if not isinstance(value, TemplateVar):
            msg = "Non-TemplateVar class instance in MetaTable instance!"
            raise WebKickstartError, msg

        if self.data.has_key(key):
            self.data[key].append(value)
        else:
            self.data[key] = [value]


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
        template = configtools.config.getTemplate(self.profile)
        return ""

    def __handleIncludes(self, mc, key):
        """Handle recursive includes"""
        configs = []

        for rec in mc.parseCommands():
            if rec[0] == key:
                if len(rec) <= 1:
                    msg = "'%s' key must have one argument." % key
                    raise errors.ParseError, msg
                else:
                    tmp_mc = MetaConfig(rec[1])
                    configs.append(tmp_mc)

        # This is a change in the order of webkickstart metaconfig file
        # processing.  This is now width first!!
        for tmp_mc in configs:
            self.includeFile(tmp_mc)
            self.__handleIncludes(tmp_mc, key)


    def includeFile(self, mc):
        """Parse a solarisConfig object."""
        
        if mc in self.configs:
            msg = "Recursive '%s' loop detected." % configtools.include_key
            raise errors.ParseError, msg

        for row in t:
            self.variables.append(TemplateVar(row))

        self.configs.append(mc)
        
