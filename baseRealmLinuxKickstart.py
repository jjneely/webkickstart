#!/usr/bin/python
#
# baseRealmLinuxKickstart.py -- class to generate a kickstart from a 
#                               solarisConfig
#
# Copyright 2002-2005 NC State University
# Written by Jack Neely <slack@quackmaster.net> and
#            Elliot Peele <elliot@bentlogic.net>
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
from baseKickstart import baseKickstart
import errors
import string
import os
import security

class baseRealmLinuxKickstart(baseKickstart):
    """Based off of baseKickstart, implements kickstart features needed by 
       NCSU's Realm Linux"""

    def __init__(self, url, cfg, sc=None):
        baseKickstart.__init__(self, url, cfg, sc)

        # re-init buildOrder list
        self.buildOrder = [self.language,
                           self.install,
                           self.partition,
                           self.inputdevs,
                           self.firewall,
                           self.authConfig,
                           self.xconfig,
                           self.rootwords,
                           self.packages,
                           self.startPost,
                           self.enableUpdates,
                           self.reinstall,
                           self.admins,
                           self.sendmail,
                           self.owner,
                           self.consolelogin,
                           self.notempclean,
                           self.clusters,
                           self.department,
                           self.printer,
                           self.realmhooks,
                           self.extraPost ]


    def authConfig(self):
        return """
auth --useshadow --enablemd5 --enablehesiod --hesiodlhs .NS --hesiodrhs .EOS.NCSU.EDU --enablekrb5 --krb5realm EOS.NCSU.EDU --krb5kdc kerberos-1.ncsu.edu:88,kerberos-2.ncsu.edu:88,kerberos-3.ncsu.edu:88,kerberos-4.ncsu.edu:88,kerberos-5.ncsu.edu:88,kerberos-6.ncsu.edu:88 --krb5adminserver kerberos-master.ncsu.edu:749
"""


    def getDept(self):
        # Get the department out
        dept = None
        depttable = self.getKeys('dept')

        if len(depttable) == 1:
            if len(depttable[0]['options']) == 1:
                dept = depttable[0]['options'][0]
            else:
                raise errors.ParseError("dept key only takes 1 option")
        elif len(depttable) > 1:
            raise errors.ParseError("dept key found multiple times")

        if dept == None:
            return "ncsu"
        else:
            return dept


    def rootwords(self):
        # handles the root password and grub password
        roottable = self.getKeys('rootpw')
        grubtable = self.getKeys('grub')
        bootlocation = self.getKeys('enable', 'keepmbr')

        rootmd5 = None
        grubmd5 = None

        if len(roottable) == 1:
            if len(roottable[0]['options']) == 1:
                rootmd5 = roottable[0]['options'][0]
            else:
                raise errors.ParseError("root key only takes 1 option")
        elif len(roottable) > 1:
            raise errors.ParseError("root key found multiple times")

        if len(grubtable) == 1:
            if len(grubtable[0]['options']) == 1:
                grubmd5 = grubtable[0]['options'][0]
            else:
                raise errors.ParseError("grub key only takes 1 option")
        elif len(grubtable) > 1:
            raise errors.ParseError("grub key found multiple times")
        
        if len(bootlocation) > 0:
            loc = "partition"
        else:
            loc = "mbr"
        
        # okay now that we've error checked the hole in the wall...
        dept = self.getDept()

        if rootmd5 == None:
            rootmd5 = self.pullRoot()

        if grubmd5 == None:
            grubmd5 = self.pullGrub()

        if grubmd5 == None:
            retval = "bootloader --location %s\n" % loc
        else:
            retval = "bootloader --location %s --md5pass %s\n" % (loc, grubmd5)
        retval = "%srootpw --iscrypted %s\n" %(retval, rootmd5)
        del rootmd5
        del grubmd5

        return retval
        

    def pullRoot(self):
        # Get root MD5 crypt out of AFS
        
        roottable = self.checkKey(2, 2, 'root')
        if roottable == None:
            group = 'default'
            key = None
        else:
            group, key = roottable

        return security.rootMD5(group, key)


    def pullGrub(self):
        # Make group password same as root
        return self.pullRoot()


    def firewall(self):
        firewalltable = self.checkKey(1, 1000, 'firewall')
        firewallstatus = self.checkKey(0, 0, 'enable', 'nofirewall')

        ret = "firewall --medium --ssh --dhcp --port=afs3-callback:tcp,afs3-callback:udp,afs3-errors:tcp,afs3-errors:udp\n"

        if firewallstatus != None:
            ret = "firewall --diabled\n"
        elif firewalltable != None:
            ret = "firewall %s\n" % string.join(firewalltable)

        return ret


    def packages(self):
        # Do the packages section of the KS
        packagetable = self.getKeys('package')

        if len(packagetable) == 0:
            return "%packages\n@ NCSU Realm Kit Workstation\n"
        else:
            retval = "%packages\n"
            for package in packagetable:
                tmp = string.join(package['options'])
                retval = "%s%s\n" % (retval, tmp)

            return retval


    def enableUpdates(self):
        # Start the %post section and fill in some stuff we rarely change
        return """
# updates
realmconfig --kickstart updates --enable-updates

"""


    def admins(self):
        # admin users
        userstable = self.getKeys('enable', 'adminusers')
        lusertable = self.getKeys('enable', 'normalusers')
        dept = self.getDept()
        users = []
        admin = []
        extrausers = []

        if len(userstable) > 1:
            raise errors.ParseError("Multiple users keys found")
        if len(lusertable) > 1:
            raise errors.ParseError("Multiple localuser keys found")
        admin = self.pullUsers()
        if len(userstable) != 0:
            if len(userstable[0]['options']) == 0:
                raise errors.ParseError("users key requires arguments")
            admin.extend(userstable[0]['options'])
            extrausers.extend(userstable[0]['options'])

        if len(lusertable) == 1:
            if len(lusertable[0]['options']) == 0:
                raise errors.ParseError("localuser key requires arguments")
            for id in lusertable[0]['options']:
                users.append(id)
                extrausers.append(id)

        retval = "cat << EOF > /root/.klogin\n"
        for id in admin:
            retval = "%s%s.root@EOS.NCSU.EDU\n" % (retval, id)
        retval = "%sEOF\nchmod 400 /root/.klogin\n" % retval
        retval = "%s\ncat << EOF >> /etc/sudoers\n" % retval
        for id in admin:
            retval = "%s%s  ALL=(ALL) ALL\n" % (retval, id)
        retval = "%sEOF\nchmod 400 /etc/sudoers\n" % retval

        retval = "%srealmconfig --kickstart auth --users " % retval
        users.extend(admin)
        retval = retval + string.join(users, ',') + "\n"

        # adminusers and normalusers may get wiped out if not specially saved
        for id in extrausers:
            retval = "%secho %s >> /etc/users.local.base\n" % (retval, id)
            if id in admin:
                retval = "%secho %s/root@EOS.NCSU.EDU >> /root/.k5login.base\n" % (retval, id)
                
        return retval
    

    def pullUsers(self):
        # Get users out of AFS
        
        usertable = self.checkKey(2, 2, 'users')
        if usertable == None:
            group = 'default'
            key = None
        else:
            group, key = usertable

        return security.adminUsers(group, key)
        
     
    def sendmail(self):
        # Check for sendmail masq
        # if none...use the default of unity.ncsu.edu
        smtable = self.getKeys('enable', 'mailmasq')
        gmtable = self.getKeys('enable', 'receivemail')

        if len(smtable) > 1:
            raise errors.ParseError("Multiple mailmasq keys found")
        if len(gmtable) > 1:
            raise errors.ParseError("Multiple receivemail keys found")

        if len(smtable) > 0 and len(smtable[0]['options']) > 1:
            raise errors.ParseError("mailmasq key only takes zero or one argument")
        if len(gmtable) > 0 and len(gmtable[0]['options']) > 0:
            raise errors.ParseError("receivemail key takes no arguments")

        if len(smtable) > 0:
            if len(smtable[0]['options']) > 0:
                masq = "--masquerade " + smtable[0]['options'][0]
            else:
                masq = "--no-masq"
        else:
            masq = "--masquerade unity.ncsu.edu"

        if len(gmtable) > 0:
            daemon = "--enable-daemon"
        else:
            daemon = "--disable-daemon"
        
        retval = "realmconfig --kickstart sendmail"
        retval = "%s %s %s\n" % (retval, daemon, masq)

        return retval


    def consolelogin(self):
        # are text console treated as local users?  Default is no.
        ctable = self.getKeys('enable', 'consolelogin')

        if len(ctable) > 1:
            raise errors.ParseError("Multiple consolelogin keys found")
        if len(ctable) > 0 and len(ctable[0]['options']) > 0:
            raise errors.ParseError("consolelogin key takes no arguments")

        retval = """
# disable login on the console for non-local users
mv /etc/pam.d/login /etc/pam.d/login~
sed s/system-auth/remote-auth/ /etc/pam.d/login~ > /etc/pam.d/login
rm /etc/pam.d/login~\n
"""
        if len(ctable) == 1:
            return ""
        else:
            return retval


    def notempclean(self):
        # Default here is to inable tmpwatch
        table = self.getKeys('enable', 'notempclean')
        if len(table) > 1:
            raise errors.ParseError("Multiple notempclean keys found")
        if len(table) > 0 and len(table[0]['options']) > 0:
            raise errors.ParseError("notempclean key takes no arguments")

        if len(table) == 1:
            return ""
        else:
            return "realmconfig --kickstart tmpclean --enable-tmpclean\n"


    def clusters(self):
        # Check for clustered logins
        # defaults are "ncsu" for local and no cluster enabled for remote
        # we can completely disable by setting cluster values to "None"
        # localcluster <cluster>
        # remotecluster <cluster>

        local = self.checkKey(0, 1, 'enable', 'localcluster')
        remote = self.checkKey(0, 1, 'enable', 'remotecluster')

        if local == None:
            lcluster = "ncsu"
        elif len(local) == 0:
            lcluster = ""
        else:
            lcluster = local[0]

        if remote == None:
            rcluster = "None"
        elif len(remote) == 0:
            rcluster = ""
        else:
            rcluster = remote[0]

        if lcluster != "None":
            retval = "realmconfig --kickstart clusters --local-enable %s\n" % (lcluster)
        else:
            retval = "realmconfig --kickstart clusters --local-disable\n"
        if rcluster != "None":
            retval = "%srealmconfig --kickstart clusters --remote-enable %s\n" % (retval, rcluster)
        else:
            retval = "%srealmconfig --kickstart clusters --remote-disable\n" % (retval)

        return retval


    def department(self):
        # Set department

        dept = self.getDept()

        return "realmconfig --kickstart dept --set %s\n" % dept

    
    def printer(self):
        # set up default printer.  default is lp
        printer = self.checkKey(1, 1, 'printer')

        if printer == None:
            return "realmconfig --kickstart printing --default lp\n"
        else:
            return "realmconfig --kickstart printing --default %s\n" % printer[0]


    def realmhooks(self):
        # set up realm hooks, default is to use them
        hooks = self.checkKey(0, 0, 'enable', 'norealmcron')

        if hooks == None:
            return "realmconfig --kickstart support --enable-support\n"
        else:
            return "realmconfig --kickstart support --disable-support\n"
    

