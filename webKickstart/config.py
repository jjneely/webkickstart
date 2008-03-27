#!/usr/bin/python
#
# config.py -- Configuration class for webKickstrart
#
# Copyright 2003-2007 NC State University
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

# New config file notes:
# [main] section:
# logfile, loglevel
# generic_ks=profile -- when we don't know about the client
# config_collision_detection
# disable_version_case_sensitivity
# configs=dir
#
# [default]
# Sane defaults for profile sections
# plugins=foo bar baz
# required_keys = foo bar baz
# optional_keys = joe sue jane
# 
# [<profile name>]
#

class Configuration(object):

    # Default location of main config file
    defaultDir = "/etc/webkickstart"
    defaultConfig = "webkickstart.conf"

    # Global configuration defualts
    logfile = '/var/log/webkickstart.log'
    log_level = 1

    enable_security = 0
    enable_generic_ks = 0
    enable_config_collision_detection = 0
    disable_version_case_sensitivity = 0
    jumpstarts = "./configs"
    profiles = "./profiles"

    include_key = 'use'
    profile_key = 'version'  # Will select the profile/template used

    # Global Flags
    init_logging = True

    def __init__(self, configDir=None):
        # Configfiles for all plugins and webkickstart are in configDir
        # Default to /etc/webkickstart/webkickstart.conf
        if configDir:
            dir = configDir
        else:
            dir = self.defaultConfig

        file = os.path.join(dir, self.defaultConfig)

        if not os.path.exists(file):
            msg = "Missing config file: %s" % file
            raise errors.AccessError(msg)

        if not os.access(file, os.R_OK):
            msg = "Cannot read config file %s." % file
            raise errors.AccessError(msg)

        self.__dir = dir
        self.__file = file
        self.__cfg = None     # ConfigParser object
        self.reload()

    def __getattr__(self, attr):
        # Override the default getattr behavior to pull info from
        # the [main] section of the master config.
        pass

    def __checkConfig(self):
        # Test and see if we need to reload
        pass

    def pluginDict(self, profile):
        # Return a dict of keyword => function for a specific profile
        # so the config line turns into a function call
        # keyword arg1 arg2 arg3 => function("arg1", "arg2", "arg3")
        pass

    def getTemplate(self, profile):
        # Return the template for the specified version/profile
        pass

    def reload(self):
        # call to reload the config on file change
        pass




class webksconf(ConfigParser.ConfigParser):

    init_logging = True
    
    def __init__(self, configfile=['/etc/solaris2ks.conf',
                                   './solaris2ks.conf']):
        ConfigParser.ConfigParser.__init__(self)
        
        self.cfg_file = []

        # resolve non-absoulte paths relative to the directory containing
        # the web-kickstart code.  Fixes CWD dependancies.
        if type(configfile) is not type([]):
            configfile = [configfile]
        for p in configfile:
            if not os.path.isabs(p):
                p = os.path.join(sys.path[0], p)
            self.cfg_file.append(p)

        self.read(self.cfg_file)
        if self.sections() == []:
            raise errors.AccessError("Can't access %s\nCWD: %s" % \
                    (self.cfg_file, os.getcwd()))

        #setup defualts
        self.logfile = '/var/log/solaris2ks.log'
        self.debug_level = 0
        self.log_level = 0
        self.error_level = 2

        self.enable_security = 0
        self.enable_generic_ks = 0
        self.enable_config_collision_detection = 0
        self.disable_version_case_sensitivity = 0
        self.jumpstarts = "./configs"
        self.rhnkey = "No key set in configuration"

        self.defaultkey = None

        self.xmlrpc = None
        self.secret = None

        # paths to key files (for RLMTools)
        self.privatekey = self._getoption('main', 'privatekey')
        self.publickey = self._getoption('main', 'publickey')

        # directory trusted admins can leave keys for importing into RLMTools
        self.key_directory = self._getoption('main', 'key_directory')

        self.db = {}
        self.db['host'] = 'localhost.localdomain'
        self.db['user'] = 'solaris2ks'
        self.db['passwd'] = 'solaris2ks'
        self.db['db'] = 'solaris2ks'

        self.versionMap = {}

        if self._getoption('main','logfile') != None:
            self.logfile = self._getoption('main','logfile')
        if self._getoption('main','log_level') != None:
            self.log_level = int(self._getoption('main','log_level'))
        if self.init_logging:
            self.initLogging()
            
        if self._getoption('main','jumpstarts') != None:
            self.jumpstarts = self._getoption('main','jumpstarts')
        if self._getoption('main','debug_level') != None:
            self.debug_level = self._getoption('main','debug_level')
        if self._getoption('main','error_log') != None:
            self.error_log = self._getoption('main','error_log')

        if self._getoption('main','enable_security') != None:
            self.enable_security = int(self._getoption('main','enable_security'))
        if self._getoption('main','enable_generic_ks') != None:
            self.enable_generic_ks = int(self._getoption('main','enable_generic_ks'))
        if self._getoption('main','enable_config_collision_detection') != None:
            self.enable_config_collision_detection = int(self._getoption('main','enable_config_collision_detection'))
        if self._getoption('main','disable_version_case_sensitivity') != None:
            self.disable_version_case_sensitivity = int(self._getoption('main','disable_version_case_sensitivity'))
        if self._getoption('main','rhnkey') != None:
            self.rhnkey = self._getoption('main','rhnkey')

        if self._getoption('main','defaultkey') != None:
            self.defaultkey = self._getoption('main','defaultkey')

        if self._getoption('main','xmlrpc') != None:
            self.xmlrpc = self._getoption('main','xmlrpc')
        else:
            raise errors.ConfigError('Missing required "xmlrpc" location.')
        if self._getoption('main','secret') != None:
            self.secret = self._getoption('main','secret')
        else:
            raise errors.ConfigError('Missing required "secret" for XMLRPC API.')

        self.db = {}
        if self.has_section('db'):
            for option in self.options('db'):
                self.db[option] = self._getoption('db',option)
        else:
            self.enable_security = 0
        
        # Require "default" section
        if not self.has_section("default"):
            raise errors.ConfigError('A "default" section is required.')
        
        # make sure default is first in the list
        # this enables the default to be parsed first so we can
        # refer to the default in other sections
        sections = self.sections()
        sections.remove("default")
        sections.insert(0, "default")

        for section in sections:
            if section != 'main' and section != 'db':
                name = section
                if self.disable_version_case_sensitivity and name != 'default':
                    name = name.upper()
                if self._getoption(section, 'version') != None:
                    version = self._getoption(section, 'version')
                else:
                    raise errors.ParseError('No version string in section %s of'
                                            ' the config file' % (section))

                if self._getoption(section, 'nfs_path') != None:
                    nfs_path = self._getoption(section, 'nfs_path')
                    if self._getoption(section, 'nfs_server') != None:
                        nfs_server = self._getoption(section, 'nfs_server')
                    else:
                        nfs_server = self._getdefault('nfs_server')
                else:
                    nfs_server = ""
                    nfs_path = ""

                if self._getoption(section, 'ftp_path') != None:
                    ftp_path = self._getoption(section, 'ftp_path')
                    if self._getoption(section, 'ftp_server') != None:
                        ftp_server = self._getoption(section, 'ftp_server')
                    else:
                        ftp_server = self._getdefault('ftp_server')
                else:
                    ftp_server = ""
                    ftp_path = ""

                if self._getoption(section, 'http_path') != None:
                    http_path = self._getoption(section, 'http_path')
                    if self._getoption(section, 'http_server') != None:
                        http_server = self._getoption(section, 'http_server')
                    else:
                        http_server = self._getdefault(section, 'http_server')
                else:
                    http_server = ""
                    http_path = ""

                if nfs_server == "" and ftp_server == "" and http_server == "":
                    raise errors.ConfigError('No install servers defined for %s'
                                             % (section))

                if self._getoption(section, 'install_method') != None:
                    install_method = self._getoption(section, 'install_method')
                    if install_method != 'nfs' and install_method != 'ftp' and install_method != 'http':
                        raise errors.ConfigError('Invalid install method %s' % (install_method))
                elif self._getdefault('install_method') != None:
                    install_method = self._getdefault('install_method')
                else:
                    install_method = 'ftp'
                    
                module = self._getoption(section, 'module')
                module_class = self._getoption(section, 'module_class')
                if module == None or module_class == None:
                    if name == 'default':
                        module = 'baseKickstart'
                        module_class = 'baseKickstart'
                    else:
                        module = self._getdefault('module')
                        module_class = self._getdefault('module_class')

                # If this is None then that's what we want.  IN's are optional.
                rhIN = self._getoption(section, 'rhin')
                if rhIN == None:
                    if section == 'default':
                        rhIN = None
                    else:
                        rhIN = self._getdefault('rhin')

                if self._getoption(section, 'repos') == None:
                    if section == 'default':
                        repos = []
                    else:
                        repos = self._getdefault('repos')
                else:
                    repos = self._getoption(section, 'repos').split()

                self.versionMap[name] = {}
                self.versionMap[name]['version'] = version
                self.versionMap[name]['nfs_server'] = nfs_server
                self.versionMap[name]['nfs_path'] = nfs_path
                self.versionMap[name]['ftp_server'] = ftp_server
                self.versionMap[name]['ftp_path'] = ftp_path
                self.versionMap[name]['http_server'] = http_server
                self.versionMap[name]['http_path'] = http_path
                self.versionMap[name]['install_method'] = install_method
                self.versionMap[name]['module'] = module
                self.versionMap[name]['module_class'] = module_class
                self.versionMap[name]['rhin'] = rhIN
                self.versionMap[name]['repos'] = repos


    def _getoption(self, section, option):
        try:
            return self.get(section, option)
        except ConfigParser.NoSectionError, e:
            raise errors.ConfigError('Failed to find section: %s' % (section))
        except ConfigParser.NoOptionError, e:
            return None


    def _getdefault(self, key):
        if self.versionMap.has_key('default'):
            if self.versionMap['default'].has_key(key):
                return self.versionMap['default'][key]
            else:
                return None
        else:
            raise errors.ConfigError('No default section in configuration')


    def get_obj(self, name, args):
        if self.disable_version_case_sensitivity and name != 'default':
            name = name.upper()
        if name not in self.versionMap.keys():
            raise errors.ConfigError("Version %s is not defined" % name)

        module = self.versionMap[name]['module']
        module_class = self.versionMap[name]['module_class']
        url = args['url']
        sc = args['sc']

        # Suck in arbitrary module and class.  Instantiate and return
        pmod = __import__(module, globals(), locals(), [])
        pclass = getattr(pmod, module_class)
        obj = pclass(url, self.versionMap[name], sc)
        return obj


    def initLogging(self):
        logger = logging.getLogger("webks")
        
        handler = logging.FileHandler(self.logfile)
        # Time format: Jun 24 10:16:54
        formatter = logging.Formatter('%(asctime)s WK %(levelname)s: %(message)s',
                                      '%b %2d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(self.log_level)

        logger.info("Logging initialized.")

        self.init_logging = False
                                

# Global copy for all modules
config = webksconf()

