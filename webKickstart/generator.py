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
import os
import logging
from types import *

from genshi.template import TemplateLoader
from genshi.template import NewTextTemplate

# WebKickstart imports
import configtools
import plugins
from metaparser import MetaParser
from errors import *
from templatevar import TemplateVar

log = logging.getLogger("webks")

class Generator(object):

    tLoader = TemplateLoader(default_class=NewTextTemplate, allow_exec=True)

    def __init__(self, profile, mc=None, debug=False):
        assert configtools.config != None

        self.__debug = debug
        self.profile = profile
        self.configs = []
        self.variables = {}     # The dictionary that is presented to the
                                # genshi template.  Order perserved in
                                # the TemplateVar class.

        if configtools.config.findProfile(self.profile) == None:
            log.info("Requested profile not defined: %s" % self.profile)
            msg = "The profile \"%s\" is not defined." % self.profile
            raise WebKickstartError, msg

        if mc != None:
            self.__includeFile(mc)
            self.__handleIncludes(mc, configtools.config.include_key)

    def makeKickstart(self, fqdn, excludePlugins=[]):
        """Return a string of a Red Hat Kickstart."""

        file = configtools.config.getTemplate(self.profile)

        if file == None:
            msg = "The Genshi template for the '%s' profile does not exist."
            msg = msg % self.profile
            raise WebKickstartError, msg
   
        # webkickstart namespaces
        d = configtools.config.getProfileVars(self.profile)
        # TemplateVar up all the stuff from the config file
        for k in d.keys():
            self.variables[k] = TemplateVar(d[k], key=k)

        self.variables['webKickstart'] = TemplateVar('webKickstart')
        self.variables['webKickstart'].setMember('remoteHost', fqdn)
        self.variables['webKickstart'].setMember('templates', 
                configtools.config.profiles)
        self.variables['WebKickstartError'] = WebKickstartError
        self.variables['ParseError'] = ParseError

        self.buildPostVar()
        self.runPlugins()

        log.debug("Loading template file: %s" % file)
        #log.debug("Template vars: %s" % str(self.variables))
        ##built = self.__getCachedTemplate(file)
        built = self.tLoader.load(file)
        stream = built.generate(**self.variables)
        
        #s = str(built(namespaces=[configvars, self.variables, other]))
        return stream.render()

    def runPlugins(self):
        mods = plugins.getModules(plugins.WebKickstartPlugin)
        requestedPlugins = configtools.config.getPlugins(self.profile)

        for p in requestedPlugins:
            if not mods.has_key(p):
                log.error("Could not find plugin: %s" % p)
                continue

            try:
                log.debug("Running plugin: %s" % p)
                cfg = configtools.config.getPluginConf(p)
                obj = mods[p](self.variables, cfg, self.__debug)
                newvars = obj.run()
            except WebKickstartError, e:
                # User plugin raised a WebKickstart exception...we assume
                # this is what they want to do
                raise
            except Exception, e:
                # Radom error...eat it and continue
                # XXX: Need better logging of exception here
                log.error("Exception during execution of plugin: %s" % p)
                log.error('\t' + str(e))
                continue

            if isinstance(newvars, dict):
                self.variables = newvars
            else:
                log.error("Plugin return non-dictionary.")
                log.error("Ignoring plugin: %s" % p)

    def buildPostVar(self):
        # Attach %posts found in config files
        scriptlist = []
        for mc in self.configs:
            scriptlist.extend(mc.getPosts())

        scriptlist.reverse()
        webks = self.variables['webKickstart']
        if len(scriptlist) == 0:
            webks.setMember('scripts', '')
            return # No scripts

        for script in scriptlist:
            if webks.hasMember('scripts'):
                webks.scripts.append(script)
            else:
                webks.setMember('scripts', script)

    def __handleIncludes(self, mc, key):
        """Handle recursive includes"""
        configs = []

        for rec in mc.parseCommands():
            if rec[0] == key:
                if len(rec) <= 1:
                    msg = "'%s' key must have one argument." % key
                    raise errors.ParseError, msg
                else:
                    tmp_mc = MetaParser(rec[1])
                    configs.append(tmp_mc)

        # This is a change in the order of webkickstart metaconfig file
        # processing.  This is now depth first!!
        for tmp_mc in configs:
            self.__includeFile(tmp_mc)
            self.__handleIncludes(tmp_mc, key)


    def __includeFile(self, mc):
        """Parse a solarisConfig object."""
        
        if mc in self.configs:
            msg = "Recursive '%s' loop detected." % \
                    configtools.config.include_key
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
        
