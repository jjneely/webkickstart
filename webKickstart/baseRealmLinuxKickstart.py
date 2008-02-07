#!/usr/bin/python
#
# baseRealmLinuxKickstart.py -- class to generate a kickstart from a 
#                               solarisConfig
#
# Copyright 2002-2005 NC State University
# Written by Jack Neely <jjneely@pams.ncsu.edu> and
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
from config import config
from StringIO import StringIO
import errors
import os
import os.path
import re
import security

class baseRealmLinuxKickstart(baseKickstart):
    """Based off of baseKickstart, implements kickstart features needed by 
       NCSU's Realm Linux"""

    def __init__(self, url, cfg, sc=None):
        baseKickstart.__init__(self, url, cfg, sc)

        # re-init buildOrder list
        self.buildOrder = [self.language,
                           self.install,
                           self.yumRepos,
                           self.installationNumber,
                           self.rhel5Features,
                           self.partition,
                           self.selinux,
                           self.inputdevs,
                           self.firewall,
                           self.authConfig,
                           self.xconfig,
                           self.rootwords,

                           # End of command section
                           self.kickstartIncludes,
                           self.packages,
                           self.startPost,
                           self.enableUpdates,
                           self.audit,
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
                           self.staticIP,
                           self.RHN,
                           self.runUpdates,
                           self.extraFixes,
                           self.extraPost ]


    def authConfig(self):
        return """
auth --useshadow --enablemd5 --enableldap --ldapserver ldap.ncsu.edu --ldapbasedn dc=ncsu,dc=edu --enablecache --enablekrb5 --enablekrb5kdcdns --krb5realm EOS.NCSU.EDU
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
        retval = "%srootpw --iscrypted %s\n\n" %(retval, rootmd5)
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

        ret = "firewall --enabled --ssh --port=afs3-callback:tcp,afs3-callback:udp,afs3-errors:tcp,afs3-errors:udp\n"

        if firewallstatus != None:
            ret = "firewall --diabled\n"
        elif firewalltable != None:
            ret = "firewall %s\n" % " ".join(firewalltable)

        return ret


    def _magicGroup(self, groups, exclusions=[], selected=[]):
        """Return an expansion of our workstation or server groups."""
        buf = ""
        for group in groups:
            buf = "%s@ %s\n" % (buf, group)

        for pkg in exclusions:
            if pkg not in selected:
                buf = "%s-%s\n" % (buf, pkg)

        return buf


    def packages(self):
        # What are the magic groups?
        serverGroup = re.compile("@.*[Rr]ealm.*[Ss]erver$")
        workstationGroup = re.compile("@.*[Rr]ealm.*[Ww]orkstation$")

        # What packages do we need to exclude (packages)
        exclusions  = ['logwatch',    # We don't need these emails by default
                       'yum-updatesd', # Turn off new package notification
                      ]

        # Define a server (by comps groups)
        server      = ['realmlinux-base',
                       'editors',
                       'base',
                       'text-internet',
                       'legacy-software-support',
                       'system-tools',
                       'admin-tools',
                       'base-x',
                       'java',
                      ]

        # Define a Workstation (by comps groups)
        workstation = ['realmlinux-base',
                       'realmlinux-devel',
                       'authoring-and-publishing',
                       'eclipse',
                       'editors',
                       'engineering-and-scientific',
                       'games',
                       'graphical-internet',
                       'graphics',
                       'office',
                       'sound-and-video',
                       'text-internet',
                       'gnome-desktop',
                       'kde-desktop',
                       'development-libs',
                       'development-tools',
                       'gnome-software-development',
                       'java-development',
                       'kde-software-development',
                       'legacy-software-development',
                       'ruby',
                       'x-software-development',
                       'admin-tools',
                       'java',
                       'legacy-software-support',
                       'system-tools',
                       'workstation',
                       'base-x',
                      ]
        
        packagetable = self.getKeys('package')

        if len(packagetable) == 0:
            return "%packages\n" + self._magicGroup(workstation, 
                                                    exclusions) + "\n"
        else:
            retval = "%packages\n"
            selected = []
            for package in packagetable:
                tmp = ' '.join(package['options']).strip()
                selected.append(tmp)

            for selection in selected:
                if serverGroup.match(selection) != None:
                    buf = self._magicGroup(server, exclusions, selected)
                elif workstationGroup.match(selection) != None:
                    buf = self._magicGroup(workstation, exclusions, selected)
                else:
                    buf = selection + '\n'

                retval = "%s%s" % (retval, buf)

            return retval


    def enableUpdates(self):
        # Start the %post section and fill in some stuff we rarely change
        return """
# updates
realmconfig --kickstart updates --enable-updates

"""


    def audit(self):
        # kill auditd with a big hammer unless anyone really wants to use it
        audittable = self.getKeys('enable', 'audit')
        if len(audittable) > 1:
            raise errors.ParseError('Multiple audit keys found')
        elif len(audittable) == 1:
            retval = """
# make sure audit is on
chkconfig auditd on

"""
        else:
            retval = """
# turn off audit and wax any logs
chkconfig auditd off
rm -rf /var/log/audit
rm -rf /var/log/audit.d/*

"""
        return retval            


    def admins(self):
        # admin users
        userstable = self.getKeys('enable', 'adminusers')
        lusertable = self.getKeys('enable', 'normalusers')
        dept = self.getDept()
        users = []
        admin = []
        extrausers = []

        if len(userstable) > 1:
            raise errors.ParseError("Multiple 'enable adminusers' keys found")
        if len(lusertable) > 1:
            raise errors.ParseError("Multiple 'enable normalusers' keys found")
        admin = self.pullUsers()
        if len(userstable) != 0:
            if len(userstable[0]['options']) == 0:
                raise errors.ParseError("'enable adminusers' key requires arguments")
            admin.extend(userstable[0]['options'])
            extrausers.extend(userstable[0]['options'])

        if len(lusertable) == 1:
            if len(lusertable[0]['options']) == 0:
                raise errors.ParseError("'enable normalusers' key requires arguments")
            for id in lusertable[0]['options']:
                users.append(id)
                extrausers.append(id)

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
        retval = retval + ','.join(users) + "\n"

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
# RL4.4 and below don't have this code so we need to case that out
if realmconfig --kickstart pamconf --disable-console-login | grep "No such module"; then
    mv /etc/pam.d/login /etc/pam.d/login~
    sed s/system-auth/remote-auth/ /etc/pam.d/login~ > /etc/pam.d/login
    rm /etc/pam.d/login~
fi\n
"""
        if len(ctable) == 1:
            return """
# Enable console login by non-local users
# RL4.4 and below don't have this code, however this is the default anyway
realmconfig --kickstart pamconf --enable-console-login || true
"""
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
   
   
    def RHN(self):
        buf = StringIO()
        key = self.checkKey(1, 1, "enable", "activationkey")
        if key == None:
            key = config.rhnkey
        else:
            key = key[0]

        if self.sc != None:
            fqdn = os.path.basename(self.sc.filename)
            buf.write("""
# The registration program's not smart enough to figure out the host name
# with out this the profile reads "localhost.localdomain"
FQDN="%s"
""" % fqdn)
        else:
            buf.write("""
# The registration program's not smart enough to figure out the host name
# with out this the profile reads "localhost.localdomain"
IP=`/sbin/ifconfig $KSDEVICE | /bin/awk '/inet/ && !/inet6/ {sub(/addr:/, ""); print $2}'`
FQDN=`python -c "import socket; print socket.getfqdn('$IP')"`
""")

        buf.write("""/usr/sbin/rhnreg_ks --activationkey %s --profilename $FQDN --serverUrl https://rhn.linux.ncsu.edu/XMLRPC --sslCACert /usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT
""" % key)

        buf.write("""# Import the RPM GPG keys
if [ -f /usr/share/rhn/RPM-GPG-KEY ] ; then
    /bin/rpm --import /usr/share/rhn/RPM-GPG-KEY
fi
if [ -f /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release ] ; then
    /bin/rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
fi
if [ -f /usr/share/realmconfig/realmkit.gpg ] ; then
    /bin/rpm --import /usr/share/realmconfig/realmkit.gpg
fi
if [ -f /usr/share/realmconfig/data/realmkit.gpg ] ; then
    /bin/rpm --import /usr/share/realmconfig/data/realmkit.gpg
fi

# Set Up2Date Configuration
if [ -f /usr/share/realmconfig/default-modules/up2date.py ] ; then
    /usr/bin/python /usr/share/realmconfig/default-modules/up2date.py -f
fi
""")

        return buf.getvalue()

    def runUpdates(self):
        return """
# Run Yum update
chvt 3
/usr/bin/yum -y update yum
/usr/bin/yum -y update
chvt 1
""" 

    def extraFixes(self):
        return """# Final Fixes for RHEL 5
# Fix for Red Hat Bug #236669
mv /etc/nsswitch.conf /etc/nsswitch.conf~
cat /etc/nsswitch.conf~ | sed 's/^protocols.*files ldap/protocols:  files/' \
        > /etc/nsswitch.conf
rm -f /etc/nsswitch.conf~
"""

