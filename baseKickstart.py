#!/usr/bin/python
#
# baseKickstart.py -- class to generate a kickstart from a solarisConfig
#
# Copyright, 2002 Jack Neely <slack@quackmaster.net>
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
import exceptions
import string
import os

class baseKickstart:
    """Base class for generating a kickstart from a solarisConfig.  To be
       subclassed
       to handle multiple versions although this class should be successful at 
       generating a kickstart for the RK7.3."""
       
    table = []
    callOrder = []
    configs = []
    
    def __init__(self, sc=None):
        if not sc == None:
            self.includeFile(sc)
        
        
    def includeFile(self, sc):
        """Parse a solarisConfig object."""
        
        self.mergeTable(sc.parseCommands())
        self.configs.append(sc)
        
    
    def mergeTable(self, t):
        """Merge a table from a solarisConfig into the current table.
           This does a streigh merge without spacial cases for part and
           package."""
        
        for rec in t:
            # For part and package we just append as we allow
            # multiple entries for both keys
            if rec['key'] != 'part' and rec['key'] != 'package':
                for rec2 in self.table:
                    # if key is not part or package then we let an identical
                    # key from imported file override a present key.
                    if rec['key'] == rec2['key'] and rec['enable'] == rec2['enable']:
                        self.table.remove(rec2)
            
            self.table.append(rec)
        
            
    def getKeys(self, key, enable=None):
        # Return a list of matching keys
        list = []
        for rec in self.table:
            if enable == None:
                if rec['key'] == key:
                    list.append(rec)
            else:
                if rec['key'] == 'enable' and rec['enable'] == enable:
                    list.append(rec)

        return list


    def checkKey(self, min_argc, max_argc, key, enable=None):
        # Get the matching key with getKeys() and do my basic
        # error checking so I don't have to do it in every function.
        # We check that we have the proper # of arguments, that there's
        # only one matching key, and that arg ezists.
        # If key exists we return a list of its args, otherwise we
        # return None.
        table = self.getKeys(key, enable)

        if len(table) <= 0:
            return None
        
        if not enable == None:
            strkey = "%s %s" % (key, enable)
        else:
            strkey = key
                
        if len(table) > 1:
            raise exceptions.ParseError("Multiple %s keys found" % strkey)

        argc = len(table[0]['options'])
        if argc < min_argc:
            raise exceptions.ParseError("%s key has too few arguments"%strkey)
        if argc > max_argc:
            raise exceptions.ParseError("%s key has too many arguments"%strkey)

        return table[0]['options']
    

    def makeKS(self):
        """Return a string containing a RHL kickstart."""
        
        return ""
        
        
    def language(self):
        # Return stirng that defines the language parts of ks
        langtable = self.getKeys('lang')
        langstable = self.getKeys('langs')
        
        if len(langtable) > 1:
            raise exceptions.ParseError("lang key found multiple times")
        if len(langtable) > 0 and len(langtable[0]['options']) != 1:
            raise exceptions.ParseError("lang key found with improper number of options")
        if len(langstable) > 1:
            raise exceptions.ParseError("langs key found multiple times")
        if len(langstable) > 0 and not len(langstable[0]['options']) > 0:
            raise exceptions.ParseError("langs key found with improper number of options")

        if len(langtable) > 0:
            lang = langtable[0]['options'][0]
        else:
            lang = "en_US"

        if len(langstable) > 0:
            tmp = string.join(langstable[0]['options'])
            langs = "--default %s %s" % (lang, tmp)
        else:
            langs = "--default %s %s" % (lang, lang)

        retval = "lang %s\nlangsupport %s\n\n" % (lang, langs)
        return retval


    def install(self):
        # network, install, and method parts of KS
        retval = "install\nnetwork --bootproto dhcp\n"

        installtable = self.getKeys('src')
        if len(installtable) > 1:
            raise exceptions.ParseError("The src key is found multiple times")
        if len(installtable) > 0 and len(installtable[0]['options']) != 1:
            raise exceptions.ParseError("The src key takes one option only")

        if len(installtable) > 0:
            src = installtable[0]['options'][0]
        else:
            src = "ftp"
        if src == "ftp":
            url = "url --url ftp://kickstart.linux.ncsu.edu/pub/realmkit/7.3/i386"
        elif src == "nfs":
            url = "nfs --server kickstart.linux.ncsu.edu --dir /export/realmkit-7.3"
        else:
            raise exceptions.ParseError("Invalid option to src key")

        retval = "%s%s\n\n" %(retval, url)
        return retval



    def partition(self):
        # Return partition information
        retval = "zerombr yes\nclearpart --all\n"

        parttable = self.getKeys('part')
        # We are just going to take what's in the cfg file and go with it
        if len(parttable) == 0:
            parts = """
part / --size 4072
part swap --recommended
part /boot --size 50
part /tmp --size 256 --grow 
part /var --size 256
part /var/cache --size 256
"""
        else:
            parts = ""
            for row in parttable:
                tmp = "part " + string.join(row['options'])
                parts = "%s%s\n" % (parts, tmp)

        retval = "%s%s" % (retval, parts)
        return retval


    def inputdevs(self):
        # Mostly stuff here we don't modify
        # we don't support USB mice yet...
        mousetable = self.getKeys('enable', '3bmouse')

        if len(mousetable) > 0:
            retval = "mouse generic3ps/2\n"
        else:
            retval = "mouse --emulthree genericps/2\n"

        retval = "timezone US/Eastern\nkeyboard us\nreboot\n" + retval
        retval = retval + """
auth --useshadow --enablemd5 --enablehesiod --hesiodlhs .NS --hesiodrhs .EOS.NCSU.EDU --enablekrb5 --krb5realm EOS.NCSU.EDU --krb5kdc kerberos-1.eos.ncsu.edu:88,kerberos-2.eos.ncsu.edu:88,kerberos-3.eos.ncsu.edu:88,kerberos-4.unity.ncsu.edu:88 --krb5adminserver kerberos.eos.ncsu.edu:749

firewall --medium --ssh --dhcp
"""

        return retval


    def xconfig(self):
        # Define the xconf line
        xtable = self.getKeys('enable', 'nox')

        if len(xtable) > 0:
            retval = "skipx\n"
        else:
            retval = 'xconfig --hsync 31.5-57.0 --vsync 50-90 --startxonboot --resolution "1152x864" --depth 16\n'

        return retval


    def getDept(self):
        # Get the department out
        dept = None
        depttable = self.getKeys('dept')

        if len(depttable) == 1:
            if len(depttable[0]['options']) == 1:
                dept = depttable[0]['options'][0]
            else:
                raise exceptions.ParseError("dept key only takes 1 option")
        elif len(depttable) > 1:
            raise exceptions.ParseError("dept key found multiple times")

        if dept == None:
            return "pams"
        else:
            return dept

        
    def rootwords(self):
        # handles the root password and grub password
        roottable = self.getKeys('root')
        grubtable = self.getKeys('grub')

        rootmd5 = None
        grubmd5 = None

        if len(roottable) == 1:
            if len(roottable[0]['options']) == 1:
                rootmd5 = roottable[0]['options'][0]
            else:
                raise exceptions.ParseError("root key only takes 1 option")
        elif len(roottable) > 1:
            raise exceptions.ParseError("root key found multiple times")

        if len(grubtable) == 1:
            if len(grubtable[0]['options']) == 1:
                grubmd5 = grubtable[0]['options'][0]
            else:
                raise exceptions.ParseError("grub key only takes 1 option")
        elif len(grubtable) > 1:
            raise exceptions.ParseError("grub key found multiple times")
        
        # okay now that we've error checked the hole in the wall...
        dept = self.getDept()

        if rootmd5 == None:
            rootmd5 = self.pullRoot(dept)

        if grubmd5 == None:
            retval = "bootloader --location mbr\n"
        else:
            retval = "bootloader --location mbr --md5pass %s\n" % grubmd5
        retval = "%srootpw --iscrypted %s\n" %(retval, rootmd5)
        del rootmd5
        del grubmd5

        return retval
        

    def pullRoot(self, dptname=None):
        # Get root MD5 crypt out of AFS
        # Quite heavily based off code by John Berninger
        
        conftree = '/afs/bp.ncsu.edu/system/@sys/update/'
        defaultkey = 'HZv33Q6cqj7mLPVjX6qwiPRVcqswUsbL'
        openssl = '/usr/bin/openssl'

        key = ""

        getDefault = 0
        if dptname == None:
            getDefault = 1
        else:
            if not os.access(conftree+dptname+'/root', os.R_OK):
                getDefault = 1
            elif os.access(conftree+dptname+'/update.conf', os.R_OK):
                keyline = os.popen('/bin/grep "^root\>" '+conftree+dptname+'/update.conf').read()[:-1]
                (name, key) = string.split(keyline)
            else:
                key = defaultkey

            if getDefault == 0:
                cryptroot = os.popen(openssl+' bf -d -in '+conftree+dptname+'/root -k '+key).read()[:-1]
                
                return cryptroot

        if getDefault == 1:
            #Update the default root word
            cryptroot = os.popen(openssl+' bf -d -in '+conftree+'/root -k '+defaultkey).read()[:-1]
            
            return cryptroot
        
        raise StandardError("I shouldn't have gotten here in pullRoot()")

     
    def packages(self):
        # Do the packages section of the KS
        packagetable = self.getKeys('package')

        if len(packagetable) == 0:
            return "%packages\n@ Realm Kit Workstation\n"
        else:
            retval = "%packages\n"
            for package in packagetable:
                tmp = string.join(package['options'])
                retval = "%s%s\n" % (retval, tmp)

            return retval


    def startPost(self):
        # Start the %post section and fill in some stuff we rarely change
        return """
%post
# Let's make DNS work
cat << EOF > /etc/resolv.conf
nameserver 152.1.1.206
nameserver 152.1.1.161
EOF

# Want a /.version file.
echo "Kickstarted `/bin/date +%D`" > /.version
rpm -qa | sort >> /.version

# make startup non-interactive
mv /etc/sysconfig/init /etc/sysconfig/init~
sed 's/^PROMPT=yes$/PROMPT=no/' < /etc/sysconfig/init~ > /etc/sysconfig/init
rm /etc/sysconfig/init~

# fix /etc/hosts still
(grep -v localhost /etc/hosts ; echo "127.0.0.1 localhost.localdomain   localhost") > /etc/hosts.new && mv /etc/hosts.new /etc/hosts

# updates
realmconfig --kickstart updates --enable-updates

#so apropos works
/usr/sbin/makewhatis >/dev/null 2>&1 || :

"""


    def reinstall(self):
        # Part of %post.  Configure reinstall options
        table = self.getKeys('enable', 'reinstall')

        if len(table) > 1:
            raise exceptions.ParseError("Multiple reinstall keys found")
        if len(table) == 0:
            # no enable reinstall
            # I'd do this by default but I'm not sure how to
            # "know" the ks URL to give the kernel.  Future issue.
            # XXX
            return ""

        if len(table[0]['options']) > 1:
            raise exceptions.ParseError("reinstall key only takes 1 option")

        ksline = table[0]['options'][0]
        return """
#set up a reinstall image
cd /root
ncftpget ftp://kickstart.linux.ncsu.edu/pub/realmkit/realmkit-7.3/i386/dosutils/autoboot/*
mv /root/initrd.img /boot/initrd-reinstall.img
mv /root/vmlinuz /boot/vmlinuz-reinstall.img
rm -f cdboot.img
/sbin/grubby --add-kernel=/boot/vmlinuz-reinstall.img --initrd=/boot/initrd-reinstall.img --title="Reinstall Workstation" --copy-default --args="ks=%s ramdisk_size=8192 noshell"
""" % ksline


    def admins(self):
        # admin users
        userstable = self.getKeys('users')
        lusertable = self.getKeys('enable', 'normalusers')
        dept = self.getDept()
        users = []
        admin = []

        if len(userstable) > 1:
            raise exceptions.ParseError("Multiple users keys found")
        if len(lusertable) > 1:
            raise exceptions.ParseError("Multiple localuser keys found")
        if len(userstable) == 0:
            tmp = self.pullUsers(dept)
            admin = string.split(tmp)
        else:
            if len(userstable[0]['options']) == 0:
                raise exceptions.ParseError("users key requires arguments")
            admin = userstable[0]['options']

        if len(lusertable) == 1:
            if len(lusertable[0]['options']) == 0:
                raise exceptions.ParseError("localuser key requires arguments")
            for id in lusertable[0]['options']:
                users.append(id)

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

        return retval
    

    def pullUsers(self, dptname=None):
        # Get users out of AFS
        # Quite heavily based off code by John Berninger
        
        conftree = '/afs/bp.ncsu.edu/system/@sys/update/'
        defaultkey = 'HZv33Q6cqj7mLPVjX6qwiPRVcqswUsbL'
        openssl = '/usr/bin/openssl'

        key = ""

        getDefault = 0
        if dptname == None:
            getDefault = 1
        else:
            if not os.access(conftree+dptname+'/users', os.R_OK):
                getDefault = 1
            elif os.access(conftree+dptname+'/update.conf', os.R_OK):
                keyline = os.popen('/bin/grep "^users\>" '+conftree+dptname+'/update.conf').read()[:-1]
                (name, key) = string.split(keyline)
            else:
                key = defaultkey

            if getDefault == 0:
                cryptroot = os.popen(openssl+' bf -d -in '+conftree+dptname+'/users -k '+key).read()[:-1]
                
                return cryptroot

        if getDefault == 1:
            #Update the default root word
            cryptroot = os.popen(openssl+' bf -d -in '+conftree+'/users -k '+defaultkey).read()[:-1]
            
            return cryptroot
        
        raise StandardError("I shouldn't have gotten here in pullUsers()")


     
    def sendmail(self):
        # Check for sendmail masq
        # if none...use the default of unity.ncsu.edu
        smtable = self.getKeys('enable', 'mailmasq')
        gmtable = self.getKeys('enable', 'receivemail')

        if len(smtable) > 1:
            raise exceptions.ParseError("Multiple mailmasq keys found")
        if len(gmtable) > 1:
            raise exceptions.ParseError("Multiple receivemail keys found")

        if len(smtable) > 0 and len(smtable[0]['options']) > 1:
            raise exceptions.ParseError("mailmasq key only takes zero or one argument")
        if len(gmtable) > 0 and len(gmtable[0]['options']) > 0:
            raise exceptions.ParseError("receivemail key takes no arguments")

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
            raise exceptions.ParseError("Multiple consolelogin keys found")
        if len(ctable) > 0 and len(ctable[0]['options']) > 0:
            raise exceptions.ParseError("consolelogin key takes no arguments")

        retval = """
# disable login on the console for non-local users
mv /etc/pam.d/login /etc/pam.d/login~
sed s/system-auth/remote-auth/ /etc/pam.d/login~ > /etc/pam.d/login
rm /etc/pam.d/login~
"""
        if len(ctable) == 1:
            return ""
        else:
            return retval


    def notempclean(self):
        # Default here is to inable tmpwatch
        table = self.getKeys('enable', 'notempclean')
        if len(table) > 1:
            raise exceptions.ParseError("Multiple notempclean keys found")
        if len(table) > 0 and len(table[0]['options']) > 0:
            raise exceptions.ParseError("notempclean key takes no arguments")

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
    
