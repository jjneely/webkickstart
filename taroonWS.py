#!/usr/bin/python
#
# taroonWS.py - Web-Kickstart module for Realm Linux WS3 based on
#              RHEL WS3 (Taroon)
#
# Copyright 2004 NC State University
# Written by Jack Neely <slack@quackmaster.net>
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

import baseRealmLinuxKickstart as realmLinux

import string

class taroonWS(realmLinux.baseRealmLinuxKickstart):

    def __init__(self, url, cfg, sc=None):
        realmLinux.baseRealmLinuxKickstart.__init__(self, url, cfg, sc)
        
        # modify the build order to include out functions
        # This inserts our functions before the extraPost method
        i = len(self.buildOrder) - 1
        self.buildOrder[i:i] = [self.RHN]


    def admins(self):
        # admin users
        userstable = self.getKeys('enable', 'adminusers')
        lusertable = self.getKeys('enable', 'normalusers')
        dept = self.getDept()
        users = []
        admin = []

        if len(userstable) > 1:
            raise errors.ParseError("Multiple users keys found")
        if len(lusertable) > 1:
            raise errors.ParseError("Multiple localuser keys found")
        admin = self.pullUsers()
        if len(userstable) != 0:
            if len(userstable[0]['options']) == 0:
                raise errors.ParseError("users key requires arguments")
            admin.extend(userstable[0]['options'])

        if len(lusertable) == 1:
            if len(lusertable[0]['options']) == 0:
                raise errors.ParseError("localuser key requires arguments")
            for id in lusertable[0]['options']:
                users.append(id)

        retval = "cat << EOF > /root/.k5login\n"
        for id in admin:
            retval = "%s%s/root@EOS.NCSU.EDU\n" % (retval, id)
        retval = "%sEOF\nchmod 400 /root/.k5login\n" % retval
        retval = "%s\ncat << EOF >> /etc/sudoers\n" % retval
        for id in admin:
            retval = "%s%s  ALL=(ALL) ALL\n" % (retval, id)
        retval = "%sEOF\nchmod 400 /etc/sudoers\n" % retval

        retval = "%srealmconfig --kickstart auth --users " % retval
        users.extend(admin)
        retval = retval + string.join(users, ',') + "\n"

        return retval
    

    def RHN(self):

        key = self.checkKey(1, 1, "enable", "activationkey")
        if key == None:
            key = "6ed40e5c831bd8a8d706f0abe8f44f09"
        else:
            key = key[0]
        
        return """
# The registration program's not smart enough to figure out the host name
# with out this the profile reads "localhost.localdomain"
. /etc/sysconfig/network
/bin/hostname $HOSTNAME

/usr/sbin/rhnreg_ks --activationkey %s --serverUrl https://rhn.linux.ncsu.edu/XMLRPC --sslCACert /usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT

# Import the RPM GPG keys
/bin/rpm --import /usr/share/rhn/RPM-GPG-KEY
/bin/rpm --import /usr/share/realmconfig/realmkit.gpg

# Run Up2Date
chvt 3
/usr/sbin/up2date --nox -u
sleep 60
chvt 1
""" % key
        
