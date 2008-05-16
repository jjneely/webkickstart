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
        self.table = []
        self.row = 0
        self.append(tokens)

    def __iter__(self):
    	return self
    	
    def __str__(self):
        return self.verbatim()

    def __getitem__(self, idx):
        return self.tokens[self.row][idx]

    def __setitem__(self, idx, val):
        raise WebKickstartError, "Refusing to alter values from a metaconfig."
        
    def next(self):
        if self.row >= len(self.table) - 1:
            raise StopIteration
        else:
            self.row = self.row + 1

    def reset(self):
        self.row = 0
    
    def append(self, tokens):
        if isinstance(tokens, []):
            if len(tokens) == 0:
                msg = "Refusing to add a list of 0 tokens."
                raise ParseError, msg
            self.table.append(tokens)

        elif isinstance(tokens, ""):
            self.table.append([tokens])

        else:
            msg = "Unsupported token type for TemplateVar class."
            raise WebKickstartError, msg

	def verbatim(self):
        return ' '.join(self.tokens[self.row])

    def key(self):
        return self.tokens[self.row][0]

    def options(self):
        return self.tokens[self.row][1:]

    def len(self):
        return len(self.tokens[self.row][1:])

    def records(self):
        return len(self.tokens)


class Generator(object):

    def __init__(self, profile, mc=None):
        self.profile = profile
        self.configs = []
        self.variables = {}     # The dictionary that is presented to the
                                # cheetah template.  Order perserved in
                                # the TemplateVar class.

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
            raise ParseError, msg

        for row in t:
            var = TemplateVar(row)
            if self.variables.has_key(var.key()):
                # We've created a second TemplateVar so we use the same
                # code for figuring out what the key is.  Next, toss it.
                self.variables[var.key()].append(row)
            else:
                self.variables[var.key()] = var

        self.configs.append(mc)
        
