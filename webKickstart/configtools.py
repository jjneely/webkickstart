#!/usr/bin/python
#
# config.py -- Configuration class for webKickstrart
#
# Copyright 2003-2008 NC State University
# Written by Elliot Peele <elliot@bentlogic.net>
#            Jack Neely <jjneely@pams.ncsu.edu>
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import logging
import ConfigParser
import sys
import os
import os.path
import errors

log = logging.getLogger('webks')

# New config file notes:
# [main] section:
# logfile, loglevel
# generic_ks=profile -- when we don't know about the client
# config_collision_detection
# disable_version_case_sensitivity
# configs=dir
#
# [default]
#  * Sane defaults for profile sections
# plugins=foo bar baz
# <template specific args>
# 
# [<profile name>]
# * Each template will define list of required/optional keys
# * Plugins may add additional required/optional keys
# * Templates must be smart enough to know what templateVars exported
#   by the plugins to use

# A global Configuration class instance.  
# (Must be initialized via the WebKickstart main module.)
config = None

class Parser(ConfigParser.ConfigParser):

    def get(self, section, option, default):
        try:
            return ConfigParser.ConfigParser.get(self, section, option)
        except ConfigParser.NoOptionError:
            return default


class Configuration(object):

    # Default location of main config file
    defaultDir = "/etc/webkickstart"
    defaultFile = "webkickstart.conf"

    # [main] keys that we require and their defaults
    defaultCfg = {'logfile':        '/var/log/webkickstart.log',
                  'log_level':      1,
                  'generic_ks':     0,
                  'security':       1,
                  'collision':      1,
                  'profile_case_sensitivity':   0,
                  'hosts':          './configs',
                  'profiles':       './profiles',
                  'include_key':    'use',
                  'profile_key':    'version',
                 }

    def __init__(self, configDir=None):
        # Configfiles for all plugins and webkickstart are in configDir
        # Default to /etc/webkickstart/webkickstart.conf
        if configDir:
            dir = configDir
        else:
            dir = self.defaultDir

        file = os.path.join(dir, self.defaultFile)

        if not os.path.exists(file):
            msg = "Missing config file: %s" % file
            raise errors.AccessError(msg)

        if not os.access(file, os.R_OK):
            msg = "Cannot read config file %s." % file
            raise errors.AccessError(msg)

        self.__dir = dir
        self.__file = file
        self.__cfg = {}     # ConfigParser objects
        self.__mtime = {}
        self.reload()

        self.__initLogging()
        log.debug("Using configuration file: %s" % self.__file)

    def __getattr__(self, attr):
        # Override the default getattr behavior to pull info from
        # the [main] section of the master config.
        if attr in self.defaultCfg.keys():
            self.__checkConfig()
            return self.__cfg[self.__file].get('main', attr, 
                                               self.defaultCfg[attr])
        else:
            # __getattr__ is called after the normal ways of finding
            # attrs.  So we know to end the whole mess here rather than
            # munging self.__dict__
            raise AttributeError, attr

    def __setattr__(self, attr, value):
        # For testing and more advanced configuration bits we need to
        # be able to progmatically set some config values
        # Do we try to store the changes?  Next conf file update will
        # nuke them.
        if attr in self.defaultCfg.keys():
            self.__cfg[self.__file].set('main', attr, value)
        else:
            # __setattr__ is called on every attribute assignment.  Call the
            # superclass method.
            return object.__setattr__(self, attr, value)

    def __initLogging(self, file=None, level=1):
        logger = logging.getLogger("webks")
        if len(logger.handlers) > 0:
            # we've already set something up here
            return
        
        if file == None or file == '-':
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.FileHandler(file)

        # Time format: Jun 24 10:16:54
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',
                                      '%b %2d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

        logger.info("Logging initialized.")

    def __checkConfig(self, file=None):
        # Test and see if we need to reload
        if file == None: file = self.__file

        mtime = os.stat(file).st_mtime
        if not self.__mtime.has_key(file) or mtime > self.__mtime[file]:
            self.reload(file)

    def getPlugins(self, profile):
        # Return a list of plugins used for the given profile
        self.__checkConfig()
        if not self.__cfg[self.__file].has_section(profile):
            raise errors.ConfigError, "Profile '%s' not defined." % profile

        # Use the supplied defaults
        if  self.__cfg[self.__file].has_section('default'):
            line = self.__cfg[self.__file].get('default', 'plugins', '')
        else:
            line = ""

        line = self.__cfg[self.__file].get(profile, 'plugins', line)
        return line.split()

    def getPluginConf(self, plugin):
        # Return a Parser() object with the config file for this plugin
        pass

    def getTemplate(self, profile):
        # Return the template file for the specified version/profile
        filename = os.path.join(self.profiles, '%s.tmpl' % profile)
        if not os.path.isabs(filename):
            filename = os.path.abspath(filename)

        if os.access(filename, os.R_OK):
            return filename
        else:
            log.warning("No template found for profile: %s" % profile)
            return None

    def reload(self, file=None):
        # call to reload the config on file change
        if file == None: file = self.__file

        self.__mtime[file] = os.stat(file).st_mtime
        self.__cfg[file] = Parser()
        self.__cfg[file].read(file)


