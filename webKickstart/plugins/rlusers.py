#!/usr/bin/python
#
# rlusers.py -- Root password, root users, and normal users for Realm Linux
# Copyright (C) 2008 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
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
import os
import os.path 

from webKickstart.plugins import TemplateVar
from webKickstart.plugins import WebKickstartPlugin
from webKickstart.errors  import *

log = logging.getLogger('webks')

class RealmLinuxUsersPlugin(WebKickstartPlugin):

    """
    Unencrypt the list of admin users and root password and provide
    TemplateVars for them.  Combine the lists with specified normal
    users where needed.
    """

    def run(self):
        self.doRootPW()
        self.doUsers()

        return self.variableDict

    def doRootPW(self):
        if self.variableDict.has_key('rootpw'):
            # We assume the user as provided his own root password
            return

        group = 'default'
        key = None
        if self.variableDict.has_key('root'):
            if self.variableDict['root'].len() == 2:
                group = self.variableDict['root'][0]
                key = self.variableDict['root'][1]
            else:
                msg = "The 'root' keyword requires a group name and key."
                raise ParseError, msg

        t = TemplateVar(['rootpw', self.rootMD5(group, key)])
        self.addVar(t)

    def doUsers(self):
        # Add 'realmadmins', 'realmotheradmins', 
        # 'realmusers' to variables
        group = 'default'
        key = None
        if self.variableDict.has_key('users'):
            if self.variableDict['users'].len() == 2:
                group = self.variableDict['users'][0]
                key = self.variableDict['users'][1]
            else:
                msg = "The 'users' keyword requires a group name and key."
                raise ParseError, msg

        realmadmins = self.adminUsers(group, key)
        t = TemplateVar(['realmadmins'] + realmadmins)
        self.addVar(t)
        
        if not self.haveVar('enable'):
            enable = TemplateVar('', key='enable')
        else:
            enable = self.variableDict['enable']

        if enable.hasMember('adminusers'):
            self.addVar(TemplateVar(enable.adminusers.options(), 
                                    key='realmotheradmins', noKey=True))
        else:
            self.addVar(TemplateVar([], key='realmotheradmins', noKey=True))

        if enable.hasMember('normalusers'):
            self.addVar(TemplateVar(enable.normalusers.options(), 
                                    key='realmusers', noKey=True))
        else:
            self.addVar(TemplateVar([], key='realmusers', noKey=True))


    def rootMD5(self, group, key=None):
        """Returns the MD5 Hash for the root password for this admin group
           or, on failure the default MD5 hash."""

        return self._decryptData('root.md5', group, key)


    def adminUsers(self, group, key=None):
        """Returns a list of admin users.  If the list for the admin group is 
           not found the default list will be returned."""

        data = self._decryptData('users', group, key)

        list = data.split()
        return list


    def _decryptData(self, what, group, key=None):
        """Returns a stripped string of data. what can be 'root.md5' or 'users'.
           Pulls information out of the conftree."""

        # Load up some defaults from the config
        if self.cfg is None:
            msg = "rlusers.conf config file is missing or could not be read."
            raise WebKickstartError, msg
        if not self.cfg.has_section('main'):
            msg = "rlusers.conf is missing the [main] section"
            raise WebKickstartError, msg

        defaultkey = self.cfg.get('main', 'defaultkey', None)
        conftree = self.cfg.get('main', 'conftree', None)
        openssl = '/usr/bin/openssl'

        if defaultkey is None or defaultkey == "":
            msg = "rlusers.conf must provide a 'defaultkey'"
            raise WebKickstartError, msg
        if conftree is None or conftree == "":
            msg = "rlusers.conf must provide a 'conftree'"
            raise WebKickstartError, msg
    
        if key == None:
            #print "key is None...using default"
            group = 'default'
            key = defaultkey
        else:
            # check if group exists
            path = os.path.join(conftree, what, group)
            if not os.access(path, os.R_OK):
                #print "Data file missing, using default"
                group = 'default'
                key = defaultkey
    
        path = os.path.join(conftree, what, group)
        command = "%s bf -d -k %s -in %s" % (openssl, key, path)
        pipe = os.popen(command)
        stuff = pipe.read().strip()
        ret = pipe.close()
        if not ret == None:
            # XXX: This is raised when the wrong/bad encryption key is used!!
            msg = "Blowfish decryption failed decrypting the '%s' group.  "
            msg = msg + "Perhaps you misstyped the encryption key."
            raise WebKickstartError, msg % group

        return stuff
    
