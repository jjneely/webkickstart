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

# Pythong imports
import logging
from types import *

# Cheetah
from Cheetah.Template import Template

# WebKickstart imports
import configtools
import plugins
from metaparser import MetaParser
from errors import *
from templatevar import TemplateVar

log = logging.getLogger("webks")

class Generator(object):

    def __init__(self, profile, mc=None):
        assert configtools.config != None

        self.profile = profile
        self.configs = []
        self.variables = {}     # The dictionary that is presented to the
                                # cheetah template.  Order perserved in
                                # the TemplateVar class.

        if mc != None:
            self.includeFile(mc)
            self.configs.append(mc)
            self.__handleIncludes(mc, configtools.config.include_key)

    def makeKickstart(self):
        """Return a string of a Red Hat Kickstart."""

        file = configtools.config.getTemplate(self.profile)

        if file == None:
            msg = "Profile '%s' from the '%s' key does not exist."
            msg = msg % (self.profile, configtools.config.profile_key)
            raise WebKickstartError, msg

        self.runPlugins()

        log.debug("Loading template file: %s" % file)
        log.debug("Template vars: %s" % str(self.variables))
        built = Template.compile(file=file)
        log.debug(type(built))
        # We need to cache the compiled templates and check if they've
        # changed on disk
        s = str(built(namespaces=[self.variables]))
        return s

    def runPlugins(self):
        mods = plugins.getModules()
        requestedPlugins = configtools.config.getPlugins(self.profile)

        for p in requestedPlugins:
            if not mods.has_key(p):
                log.error("Could not find plugin: %s" % p)
                continue

            try:
                log.debug("Running plugin: %s" % p)
                obj = mods[p](self.variables)
                newvars = obj.run()
            except WebKickstartError, e:
                # User plugin raised a WebKickstart exception...we assume
                # this is what they want to do
                raise
            except Exception, e:
                # Radom error...eat it and continue
                log.error("Exception during execution of plugin: %s" % p)
                log.error('\t' + str(e))

            if isinstance(newvars, dict):
                self.variables = newvars
            else:
                log.error("Plugin return non-dictionary.")
                log.error("Ignoring plugin: %s" % p)

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

        for row in mc.parseCommands():
            var = TemplateVar(row)
            if self.variables.has_key(var.key()):
                # We've created a second TemplateVar so we use the same
                # code for figuring out what the key is.  Next, toss it.
                self.variables[var.key()].append(row)
            else:
                self.variables[var.key()] = var

        self.configs.append(mc)
        
