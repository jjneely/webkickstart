#!/usr/bin/python
#
# config.py -- Configuration class for webKickstrart
#
# Copyright 2003 NC State University
# Written by Elliot Peele <ebpeele2@pams.ncsu.edu>
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

from solarisConfig import solarisConfig
import ConfigParser
import os
import string
import errors

class webksconf:
    def __init__(self, configfile=['/etc/solaris2ks.conf',
                                   './solaris2ks.conf']):
        self.cfg = ConfigParser.ConfigParser()

        self.cfg_file = configfile

        self.cfg.read(self.cfg_file)
        if self.cfg.sections() == 0:
            raise errors.AccessError("Can't access %s" % (self.cfg_file))

        #setup defualts
        self.logfile = '/var/log/solaris2ks.log'
        self.debug_level = 0
        self.log_level = 0
        self.error_level = 2

        self.enable_security = 0
        self.enable_generic_ks = 0

        self.db = {}
        self.db['host'] = 'localhost.localdomain'
        self.db['user'] = 'solaris2ks'
        self.db['passwd'] = 'solaris2ks'
        self.db['db'] = 'solaris2ks'

        self.versionMap = {}

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

        self.db = {}
        if self.cfg.has_section('db'):
            for option in self.cfg.options('db'):
                self.db[option] = self._getoption('db',option)
        else:
            self.enable_security = 0

        # make sure default is first in the list
        sections = self.cfg.sections()
        for i in range(len(sections)):
            if sections[i] == 'default':
                tmp = sections[0]
                sections[0] = sections[i]
                sections[i] = tmp

        for section in sections:
            if section != 'main' and section != 'db':
                name = section
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

                if self._getoption(section, 'module') != None and self._getoption(section, 'class') != None:
                    module = self._getoption(section, 'module')
                    module_class = self._getoption(section, 'class')
                elif name == 'default':
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
            return self.cfg.get(section, option)
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
        module = self.versionMap[name]['module']
        module_class = self.versionMap[name]['module_class']
        url = args['url']
        sc = args['sc']
        cmd = ("import %s\nobj = %s.%s('%s', %s, sc)") % (module, module, module_class, url, self.versionMap[name])
        exec(cmd)
        return obj


