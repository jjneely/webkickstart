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

# Use WatchedFileHandler from Python2.6
from logging.handlers import WatchedFileHandler

log = logging.getLogger('webks')

# A global Configuration class instance.  
# (Must be initialized via the WebKickstart main module.)
config = None

class Parser(ConfigParser.ConfigParser):

    def get(self, section, option, default):
        """
        Override ConfigParser.get: If the request option is not in the
        config file then return the value of default rather than raise
        an exception.  We still raise exceptions on missing sections.
        """
        try:
            return ConfigParser.ConfigParser.get(self, section, option)
        except ConfigParser.NoOptionError:
            return default


class Configuration(object):

    # Default location of main config file
    defaultDir = "/etc/webkickstart"
    defaultFile = "webkickstart.conf"

    # [main] keys that we require and their defaults
    # These paths are relative to defaultDir or configDir if given below
    defaultCfg = {'logfile':        '/var/log/webkickstart.log',
                  'log_level':      '1',
                  'generic_ks':     '0',
                  'security':       '1',
                  'collision':      '1',
                  'case_sensitivity':   '0',
                  'hosts':          './hosts',
                  'profiles':       './profiles',
                  'include_key':    'use',
                  'profile_key':    'version',
                  'token_key':      'token',
                  'pluginconfd':    './pluginconf.d',
                 }

    # This referes to keys in defaultCfg whose values may need to be altered
    # to reflect an absolute path based on the main configuration dir
    pathKeys = ['hosts', 'profiles', 'pluginconfd']

    def __init__(self, configDir=None):
        # Configfiles for all plugins and webkickstart are in configDir
        # Default to /etc/webkickstart/webkickstart.conf
        if configDir:
            dir = configDir
        else:
            dir = self.defaultDir

        if not os.path.isabs(dir): dir = os.path.abspath(dir)

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

        self.__initLogging(self.logfile, int(self.log_level))
        log.info("Using configuration file: %s" % self.__file)

    def __default(self, attr):
        # This returns the default value for this attr.  Done in its own
        # function as we do magical things with where the defaults are
        # based on the main config directory path.

        default = self.defaultCfg[attr]
        if attr in self.pathKeys and not os.path.isabs(default):
            return os.path.join(self.__dir, default)
        else:
            return default

    def __getattr__(self, attr):
        # Override the default getattr behavior to pull info from
        # the [main] section of the master config.
        if attr in self.defaultCfg.keys():
            self.__checkConfig()
            return self.__cfg[self.__file].get('main', attr, 
                                               self.__default(attr))
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
        
        if file == '-':
            handler = logging.StreamHandler(sys.stdout)
        elif file == None or file == "":
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = WatchedFileHandler(file)

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

    def __get(self, section, option, default):
        # Handy function to query the main config file -- NOT others
        return self.__cfg[self.__file].get(section, option, default)        

    def __getProfileInfo(self, profile, option):
        section = self.findProfile(profile)
        if section == None:
            raise errors.ConfigError, "Profile '%s' not defined." % profile

        # Include an enable flag
        enabled = self.__get(section, 'enable', '0')
        if enabled.lower() not in ['1', 'yes', 'true']:
            msg = "Profile '%s' exists bug is not enabled." % profile
            raise errors.ConfigError, msg

        # Use the supplied defaults
        if self.__cfg[self.__file].has_section('default'):
            line = self.__get('default', option, '')
        else:
            line = ""

        return self.__get(section, option, line)

    def findProfile(self, profile):
        """Returns the section name of the profile which may differ when
           case sensitivity is turned off.  If the profile isn't found we
           return None.  
        """
        
        self.__checkConfig()
        sections = self.__cfg[self.__file].sections()
        sections.remove('main')
        sections.remove('default')

        if self.isTrue('case_sensitivity'):
            if profile in sections: return profile
        else:
            for i in sections:
                if profile.lower() == i.lower(): return i

        return None


    def getProfileVars(self, profile):
        """Return a dict of var:value of extra variables from the profile's
           configuration that should be inserted into the template's
           namespace.
        """
        # XXX: We call findProfile at least twice from here...
        fltr = lambda x: [ k for k in self.__cfg[self.__file].options(x) \
                            if k.startswith('var.') ]

        section = self.findProfile(profile)
        keys = []
        if self.__cfg[self.__file].has_section('default'):
            keys.extend(fltr('default'))
        keys.extend(fltr(section))

        dict = {}
        for k in keys:
            if len(k) <= 4:
                log.warning("Configuration option badly formed: %s" % k)
                continue

            name = k[4:]
            if not dict.has_key(name):
                dict[name] = self.__getProfileInfo(profile, k)

        return dict

    def isTrue(self, attr):
        value = self.__getattr__(attr)
        if value.lower() in ['1', 'true', 'enabled']:
            return True
        else:
            return False

    def getPlugins(self, profile):
        # Return a list of plugins used for the given profile
        return self.__getProfileInfo(profile, "plugins").split()

    def getPluginConf(self, plugin):
        # Return a Parser() object with the config file for this plugin
        plugind = self.pluginconfd
        if not os.path.isabs(plugind):
            plugind = os.path.join(self.__dir, plugind)

        file = os.path.join(plugind, "%s.conf" % plugin)
        log.debug("Looking for plugin config: %s" % file)
        if not os.access(file, os.R_OK):
            log.debug("File not found: %s" % file)
            return None
        
        self.__checkConfig(file)
        return self.__cfg[file]

    def getTemplate(self, profile):
        "Return the template file for the specified version/profile."
        
        # A 'template' option for each profile can select the template file
        # to use.  We check the [default] section too, finally trying
        # <profile>.tmpl
        filename = self.__getProfileInfo(profile, 'template')
        if filename == '':
            # We don't have a default setup in the conig
            filename = '%s.tmpl' % profile

        if not os.path.isabs(filename):
            filename = os.path.join(self.__dir, self.profiles, filename)

        if os.access(filename, os.R_OK):
            return filename
        else:
            log.warning("No template found for profile: %s" % profile)
            return None

    def reload(self, file=None):
        # call to reload the config on file change
        if file == None: file = self.__file
        
        log.info("Reloading config file: %s" % file)
        self.__mtime[file] = os.stat(file).st_mtime
        self.__cfg[file] = Parser()
        self.__cfg[file].read(file)

