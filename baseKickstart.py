#!/usr/bin/python
#
# baseKickstart.py -- class to generate a kickstart from a solarisConfig
#
# Copyright 2002-2006 NC State University
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
import errors
import string
import os

class baseKickstart(object):
    """Base class for generating a kickstart from a solarisConfig.  To be
       subclassed to handle multiple versions although this class should be 
       successful at generating a kickstart for Red Hat Linux 9."""
       
    def __init__(self, url, cfg, sc=None):
        # rebind important vars to initially empty objects
        # otherwise if this class is instantiated again in the same
        # interpreter, these vars will still point to the original objects
        # that will contain data we don't want.
        self.table = []
        self.configs = []
        self.buildOrder = []
        
        # set url for reinstall
        self.url = url

        # suck in config file
        if not sc == None:
            self.includeFile(sc)

        self.cfg = cfg
        
        # suck in all includes
        self.__handleUse(sc)

        # init buildOrder list
        self.buildOrder = [self.language,
                           self.install,
                           self.partition,
                           self.selinux,
                           self.inputdevs,
                           self.firewall,
                           self.xconfig,
                           self.rootwords,
                           self.packages,
                           self.startPost,
                           self.reinstall,
                           self.admins,
                           self.owner,
                           self.notempclean,
                           self.printer,
                           self.staticIP,
                           self.extraPost ]
        

    def __handleUse(self, sc):
        """Handle recursive includes"""

        for rec in sc.parseCommands():
            if rec['key'] == 'use':
                if len(rec['options']) != 1:
                    raise errors.ParseError, "'use' key must have one argument."
                else:
                    tmp_sc = solarisConfig(rec['options'][0])
                    self.includeFile(tmp_sc)
                    self.__handleUse(tmp_sc)


    def includeFile(self, sc):
        """Parse a solarisConfig object."""
        
        if sc in self.configs:
            raise errors.ParseError, "Recursive 'use' loop detected."

        self.mergeTable(sc.parseCommands())
        self.configs.append(sc)
        
    
    def mergeTable(self, t):
        """Merge a table from a solarisConfig into the current table.
           This does a streight merge without spacial cases for part,
           package, and use."""
        
        exceptions = ['part',
                      'raid',
                      'volgroup',
                      'logvol',
                      'package',
                      'use',
                      'cluster']
        
        for rec in t:
            flag = 0

            # For part, use and package we just append as we allow
            # multiple entries for both keys
            if rec['key'] in exceptions:
                self.table.append(rec)
                continue
            
            for rec2 in self.table:
                # included configs cannot override alread present keys
                if rec['key'] == rec2['key'] and rec['enable'] == rec2['enable']:
                    flag = 1
                    break
                
            if not flag:
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
        # only one matching key, and that arg exists.
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
            raise errors.ParseError("Multiple %s keys found" % strkey)

        argc = len(table[0]['options'])
        if argc < min_argc:
            raise errors.ParseError("%s key has too few arguments"%strkey)
        if argc > max_argc:
            raise errors.ParseError("%s key has too many arguments"%strkey)

        return table[0]['options']
    

    def makeKS(self):
        """Return a string containing a RHL kickstart."""
        retval = ""

        if self.table == []:
            retval = "# This is the default kickstart -- no config file found"
            retval = retval + "\n"

        for func in self.buildOrder:
            retval = retval + func()
        
        return retval
        
        
    def language(self):
        # Return stirng that defines the language parts of ks
        langtable = self.getKeys('lang')
        langstable = self.getKeys('langs')
        
        if len(langtable) > 1:
            raise errors.ParseError("lang key found multiple times")
        if len(langtable) > 0 and len(langtable[0]['options']) != 1:
            raise errors.ParseError("lang key found with improper number of options")
        if len(langstable) > 1:
            raise errors.ParseError("langs key found multiple times")
        if len(langstable) > 0 and not len(langstable[0]['options']) > 0:
            raise errors.ParseError("langs key found with improper number of options")

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
        retval = "install\n"

        network = self.checkKey(4, 4, 'enable', 'staticip')
        if network == None:
            net = "network --bootproto dhcp\n" 
        else:
            net = "network --bootproto static --ip %s --netmask %s "
            net = net + "--gateway %s --nameserver %s\n"
            net = net % (network[0], network[1], network[2], network[3])

        retval = "%s%s" % (retval, net)

        installtable = self.getKeys('src')
        if len(installtable) > 1:
            raise errors.ParseError("The src key is found multiple times")
        if len(installtable) > 0 and len(installtable[0]['options']) != 1:
            raise errors.ParseError("The src key takes one option only")

        if len(installtable) > 0:
            src = installtable[0]['options'][0]
        else:
            src = self.cfg['install_method']
        if src == "ftp":
            url = "url --url ftp://%s/%s" % (self.cfg['ftp_server'], 
                                             self.cfg['ftp_path'])
        elif src == "nfs":
            url = "nfs --server %s --dir %s" % (self.cfg['nfs_server'],
                                                self.cfg['nfs_path'])
        elif src == "http":
            # this is default
            url = "url --url http://%s/%s" % (self.cfg['http_server'],
                                              self.cfg['http_path'])
        else:
            raise errors.ParseError("Invalid option to src key")

        retval = "%s%s\n\n" %(retval, url)
        return retval



    def partition(self):
        # Return partition information
        safepart = self.getKeys('enable', 'safepartition')
        clearpart = self.checkKey(1, 1000, "clearpart")

        retval = "zerombr yes\n"

        if clearpart is not None:
            retval = "%sclearpart %s\n" % (retval, string.join(clearpart))
        elif len(safepart) > 0:
            retval = "%sclearpart --linux\n" % retval
        else:
            retval = "%sclearpart --all\n" % retval

        parttable = self.getKeys('part')
        # We are just going to take what's in the cfg file and go with it
        if len(parttable) == 0:
            parts = """
part / --size 8192
part swap --recommended
part /boot --size 128
part /tmp --size 256 --grow 
part /var --size 1024
part /var/cache --size 1024
"""
        else:
            parts = ""
            for row in parttable:
                tmp = "part " + string.join(row['options'])
                parts = "%s%s\n" % (parts, tmp)

            #Note: The raid and lvm stuff assumes that the user understands
            #      the syntax for raid and lvm in kickstarts.
                                                                                
            raidtable = self.getKeys('raid')
            raids = ""
            for row in raidtable:
                tmp = "raid " + string.join(row['options'])
                raids = "%s%s\n" % (raids, tmp)
                                                                                
            volgrouptable = self.getKeys('volgroup')
            volgroups = ""
            for row in volgrouptable:
                tmp = "volgroup " + string.join(row['options'])
                volgroups = "%s%s\n" % (volgroups, tmp)
                                                                                
            logvoltable = self.getKeys('logvol')
            logvols = ""
            for row in logvoltable:
                tmp = "logvol " + string.join(row['options'])
                logvols = "%s%s\n" % (logvols, tmp)
                                                                                
            parts = "%s%s%s%s" % (parts, raids, volgroups, logvols)

        retval = "%s%s" % (retval, parts)
        return retval


    def selinux(self):
        # Handle selinux keys (in selinux enabled versions of anaconda we use 
        # the default)
        seloptions = self.checkKey(1, 1, 'selinux')
        if seloptions == None: return ''
        else: return "selinux %s\n" % seloptions[0]


    def inputdevs(self):
        # Mostly stuff here we don't modify
        mouseargs = self.checkKey(1, 4, 'mouse')

        if mouseargs != None:
            retval = "mouse " + string.join(mouseargs) + "\n"
        else:
            retval = "mouse --emulthree genericps/2\n"

        retval = "timezone US/Eastern\nkeyboard us\nreboot\n%s" % retval

        return retval


    def xconfig(self):
        # Define the xconf line
        noXTable = self.getKeys('enable', 'nox')

        if len(noXTable) > 0:
            retval = "skipx\n"
        else:
            xTable = self.getKeys('xconfig')

            # The default settings
            xDefaults = {'--hsync':      '31.5-80.0',
                         '--vsync':      '50-90',
                         '--resolution': '"1280x1024"',
                         '--depth':      '24'}

            # Keys that don't have values
            other = ['--startxonboot']

            if len(xTable) > 1:
                raise errors.ParseError("xconfig key found multiple times")
            elif len(xTable) == 1:
                # Keys that are valid for xconfig
                validXKeys = ['--noprobe',
                              '--card',
                              '--videoram',
                              '--monitor',
                              '--hsync',
                              '--vsync',
                              '--defaultdesktop',
                              '--startxonboot',
                              '--resolution',
                              '--depth']

                # Parse out the options
                if len(xTable[0]['options']) >= 2:
                    key = None
                    for item in xTable[0]['options']:
                        if item[0:2] == '--':
                            if key != None:
                                other.append(key)
                                key = None
                            else:
                                key = item
                        elif key in validXKeys:
                            xDefaults[key] = item
                            key = None
                        else:
                            raise errors.ParseError('invalid key in xconfig: %s' % (key))

            # Make a string from the dictionary and list
            retval = 'xconfig'
            for key in xDefaults.keys():
                retval += ' %s %s' % (key, xDefaults[key])
            retval += ' ' + ' '.join(other) + '\n'

        return retval


    def rootwords(self):
        # handles the root password and grub password
        roottable = self.getKeys('rootpw')
        grubtable = self.getKeys('grub')
        bootlocation = self.getKeys('enable', 'keepmbr')
        driveorder = self.getKeys('driveorder')

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
        
        if grubmd5 == None:
            retval = "bootloader --location %s" % loc
        else:
            retval = "bootloader --location %s --md5pass %s" % (loc, grubmd5)

        if len(driveorder) == 1:
            retval += ' --driveorder '
            for drive in driveorder[0]['options']:
                retval += '%s ' % drive
        elif len(driveorder) > 1:
            raise errors.ParseError('driveorder key found more than once')

        retval = "%s\nrootpw --iscrypted %s\n" %(retval, rootmd5)
        del rootmd5
        del grubmd5

        return retval
        

    def firewall(self):
        firewalltable = self.checkKey(1, 1000, 'firewall')
        firewallstatus = self.checkKey(0, 0, 'enable', 'nofirewall')

        ret = "firewall --medium --ssh --dhcp\n"

        if firewallstatus != None:
            ret = "firewall --disabled\n"
        elif firewalltable != None:
            ret = "firewall %s\n" % string.join(firewalltable)

        return ret


    def packages(self):
        # Do the packages section of the KS
        packagetable = self.getKeys('package')

        if len(packagetable) == 0:
            return "%packages\n@ Workstation\n"
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

# Make available the ethernet interface we are using
KSDEVICE=`cat /proc/cmdline|awk -v RS=\  -v FS== '/ksdevice=.*/ {print $2; exit}'`
if [ "$KSDEVICE" == "" ]; then 
    KSDEVICE=eth0
fi

# Want a /.version file.
echo "Kickstarted `/bin/date +%D`" > /.version
rpm -qa | sort >> /.version

# make startup non-interactive
mv /etc/sysconfig/init /etc/sysconfig/init~
sed 's/^PROMPT=yes$/PROMPT=no/' < /etc/sysconfig/init~ > /etc/sysconfig/init
rm /etc/sysconfig/init~

# fix /etc/hosts still
(grep -v localhost /etc/hosts ; echo "127.0.0.1 localhost.localdomain   localhost") > /etc/hosts.new && mv /etc/hosts.new /etc/hosts

#so apropos works
/usr/sbin/makewhatis >/dev/null 2>&1 || :

"""


    def reinstall(self):
        # Part of %post.  Configure reinstall options
        table = self.getKeys('enable', 'noreinstall')

        opts = self.checkKey(0, 0, 'enable', 'noreinstall')
        if opts == [] or self.cfg['install_method'] == 'nfs':
            # Key was not found
            return ""
        else:
            return """
#set up a reinstall image
mkdir -p /boot/install
cd /boot/install
if [ ! -f vmlinuz ] ; then
    wget %s://%s/%s/isolinux/vmlinuz
fi
if [ ! -f initrd.img ] ; then
    wget %s://%s/%s/isolinux/initrd.img
fi
/sbin/grubby --add-kernel=/boot/install/vmlinuz --title="Reinstall Workstation" --copy-default --args="ks=%s ramdisk_size=8192 noshell ksdevice=$KSDEVICE" --initrd=/boot/install/initrd.img\n
""" % (self.cfg['install_method'], 
       self.cfg['%s_server' % self.cfg['install_method']], 
       self.cfg['%s_path' % self.cfg['install_method']], 
       self.cfg['install_method'],
       self.cfg['%s_server' % self.cfg['install_method']], 
       self.cfg['%s_path' % self.cfg['install_method']], 
       self.url)


    def admins(self):
        # admin users
        usertable = self.getKeys('user')
        admintable = self.getKeys('admusers')

        retval = ""

        if len(admintable) > 1:
            raise errors.ParseError("Multiple admusers keys found")
        if len(admintable) == 1:
            if len(admintable[0]['options']) == 0:
                raise errors.ParseError("admuser key requires arguments")

            retval = "%scat << EOF >> /etc/sudoers\n" % retval
            for id in admintable[0]['options']:
                retval = "%s%s  ALL=(ALL) ALL\n" % (retval, id)
            retval = "%sEOF\nchmod 400 /etc/sudoers\n" % retval

        if len(usertable) > 0:
            for id in usertable:
                if len(id['options']) != 2:
                    raise errors.ParseError("User key requires exactly " 
                                            "two arguments")
                else:
                    retval = "%s/usr/sbin/useradd -p %s %s\n" % (retval, 
                              user['options'][1], user['options'][0])

        return retval

    
    def owner(self):
        owner = self.checkKey(1, 1, 'owner')
        if owner == None:
            return ""
        else:
            return """
# Setup forwarding for root's mail
cat << EOF >> /etc/aliases
root:       %s
EOF
/usr/bin/newaliases
""" % owner[0]


    def staticIP(self):
        # Web-Kickstart uses DHCP and will configure the client as such
        # Covert the client to a static IP setup
        key = self.checkKey(0, 0, 'staticip')
        if key == None:
            return ""
        else:
            return """
# M-DHCP to Static IP conversion hack because the Comtech[tm] DHCP server
# is not always up. Originally by Lin Osborne (ITECS).

# Figure out the relevant information about this system
IP=`/sbin/ifconfig $KSDEVICE | /bin/awk '/inet/ && !/inet6/ {sub(/addr:/, ""); print $2}'`
HOSTNAME=`/usr/bin/host $IP | /bin/awk '{sub(/\.$/, ""); print $5}'`
NETMASK=`/sbin/ifconfig $KSDEVICE | /bin/awk '/inet/ && !/inet6/ {sub(/Mask:/, ""); print $4}'`
NETWORK=`/bin/ipcalc $IP -n $NETMASK | /bin/cut -d\= -f2`
GATEWAY=`echo $NETWORK | awk -F'.' '{print $1"."$2"."$3"."$4+1}'`

# Overwrite the appropriate files (/etc/sysconfig/network and
# /etc/sysconfig/network-scripts/ifcfg-eth0) to make the system not reliant
# upon DHCP
cat << EOF > /etc/sysconfig/network
NETWORKING=yes
HOSTNAME=$HOSTNAME
GATEWAY=$GATEWAY
EOF

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-$KSDEVICE
DEVICE=$KSDEVICE
BOOTPROTO=static
IPADDR=$IP
NETMASK=$NETMASK
ONBOOT=yes
EOF
"""


    def notempclean(self):
        # Default here is to inable tmpwatch
        table = self.getKeys('enable', 'notempclean')
        if len(table) > 1:
            raise errors.ParseError("Multiple notempclean keys found")
        if len(table) > 0 and len(table[0]['options']) > 0:
            raise errors.ParseError("notempclean key takes no arguments")

        if len(table) == 1:
            return "chkconfig tmpclean off\n\n"
        else:
            return "chkconfig tmpclean on\n\n"


    def printer(self):
        # set up default printer.  default is lp
        printer = self.checkKey(1, 1, 'printer')

        if printer == None:
            return "redhat-config-printer-tui --Xdefault --queue=lp\n"
        else:
            return "redhat-config-printer-tui --Xdefault --queue=%s\n" % printer[0]


    def extraPost(self):
        # Attach %posts found in config files
        post = "\n# The following scripts provided by the Jump Start confgs.\n"

        scriptlist = []
        for sc in self.configs:
            scriptlist.append(sc.getPost())

        # Make sure %post from the top level config is last
        if len(scriptlist) > 1:
            post = post + string.join(scriptlist[1:], "\n")

        # Check if we have any posts at all
        if len(scriptlist) != 0:
            post = post + "\n" + scriptlist[0]

        return post


