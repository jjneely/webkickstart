#!/usr/bin/python
#
# generator.py - Build kickstarts from MetaConfigs
#
# Copyright 2012 NC State University
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
import os.path
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

    tLoader = TemplateLoader(default_class=NewTextTemplate, allow_exec=True,
                             auto_reload=True)

    def __init__(self, profile, mc=None, debug=False):
        assert configtools.config != None

        self.__debug = debug
        self.profile = profile
        self.configs = []       # List of tuples (depth, mc)
        self.variables = {}     # The dictionary that is presented to the
                                # genshi template.  Order perserved in
                                # the TemplateVar class.

        if configtools.config.findProfile(self.profile) == None:
            log.info("Requested profile not defined: %s" % self.profile)
            msg = "The profile \"%s\" is not defined." % self.profile
            raise WebKickstartError, msg

        if mc != None:
            self.__mcFileName = os.path.basename(mc.getFileName())
            self.__includeFile(mc)
            self.__handleIncludes(mc, configtools.config.include_key)
        else:
            self.__mcFileName = ''

    def localVars(self, fqdn):
        # Setup self.variables

        # webkickstart namespaces
        d = configtools.config.getProfileVars(self.profile)
        # TemplateVar up all the stuff from the config file
        for k in d.keys():
            self.variables[k] = TemplateVar(d[k], key=k)

        self.variables['webKickstart'] = TemplateVar('webKickstart')
        self.variables['webKickstart'].setMember('remoteHost', fqdn)
        self.variables['webKickstart'].setMember('profile', self.profile)
        self.variables['WebKickstartError'] = WebKickstartError
        self.variables['ParseError'] = ParseError

        if fqdn.lower() != self.__mcFileName.lower():
            self.variables['webKickstart'].setMember('token',
                                                     self.__mcFileName)


    def makeKickstart(self, fqdn, excludePlugins=[]):
        """Return a string of a Red Hat Kickstart."""

        file = configtools.config.getTemplate(self.profile)

        if file == None:
            msg = "The Genshi template for the '%s' profile does not exist."
            msg = msg % self.profile
            raise WebKickstartError, msg
   
        self.localVars(fqdn)
        self.buildPostVar()
        self.runPlugins()

        log.debug("Loading template file: %s" % file)
        #log.debug("Template vars: %s" % str(self.variables))
        built = self.tLoader.load(file)
        stream = built.generate(**self.variables)
        
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

        # on python 2.4 we can use key=lambda x: x[0], reverse=True
        # but I need to run on 2.3 for the time being
        # In any case, this sort MUST be stable!!
        self.configs.sort(lambda x,y: cmp(y[0], x[0]))

        for depth, mc in self.configs:
            # we just use depth for sorting
            #scriptlist.append("# Depth: %s\tMC: %s" % (depth, mc.getFileName()))
            scriptlist.extend(mc.getPosts())

        webks = self.variables['webKickstart']
        if len(scriptlist) == 0:
            webks.setMember('scripts', '')
            return # No scripts

        for script in scriptlist:
            if webks.hasMember('scripts'):
                webks.scripts.append(script)
            else:
                webks.setMember('scripts', script)

    def __handleIncludes(self, mc, key, depth=0):
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

        # Track depth so we get the %posts in the right order
        for tmp_mc in configs:
            self.__includeFile(tmp_mc, depth+1)
            self.__handleIncludes(tmp_mc, key, depth+1)


    def __includeFile(self, mc, depth=0):
        """Parse a solarisConfig object."""
        
        if self.__isSeen(mc):
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

        self.configs.append((depth, mc))
        
    def __isSeen(self, mc):
        for t in self.configs:
            if t[1] == mc:
                return True

        return False
