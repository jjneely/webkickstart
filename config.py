#!/usr/bin/python
#
# config.py -- Configuration class for webKickstrart
#
# Copyright 2003-2005 NC State University
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

import ConfigParser
import sys
import os
import os.path
import string
import errors

class webksconf(ConfigParser.ConfigParser):
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

        self.defaultkey = None

        self.db = {}
        self.db['host'] = 'localhost.localdomain'
        self.db['user'] = 'solaris2ks'
        self.db['passwd'] = 'solaris2ks'
        self.db['db'] = 'solaris2ks'

        self.versionMap = {}

        if self._getoption('main','jumpstarts') != None:
            self.jumpstarts = self._getoption('main','jumpstarts')
        if self._getoption('main','logfile') != None:
            self.logfile = self._getoption('main','logfile')
        if self._getoption('main','debug_level') != None:
            self.debug_level = self._getoption('main','debug_level')
        if self._getoption('main','log_level') != None:
            self.log_level = self._getoption('main','log_level')
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

        if self._getoption('main','defaultkey') != None:
            self.defaultkey = self._getoption('main','defaultkey')

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
        pmod = __import__(module)
        pclass = getattr(pmod, module_class)
        obj = pclass(url, self.versionMap[name], sc)
        return obj


# Global copy for all modules
config = webksconf()

