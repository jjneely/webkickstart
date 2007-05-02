#!/usr/bin/python
#
# nahant.py - Kickstart module to add backwards compatibilty for RHEL 4
#
# Copyright 2007 NC State University
# Written by Jack Neely <jjneely@pams.ncsu.edu>
#
# SDG
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

from baseRealmLinuxKickstart import baseRealmLinuxKickstart

class Kickstart(baseRealmLinuxKickstart):

    def __init__(self, url, cfg, sc=None):
        baseRealmLinuxKickstart.__init__(self, url, cfg, sc)

        self.buildOrder.remove(self.installationNumber)
        self.buildOrder.remove(self.rhel5Features)
        self.buildOrder.remove(self.yumRepos)
    
    def language(self):
        langtable = self.getKeys('lang')
        
        if len(langtable) > 1:
            raise errors.ParseError("lang key found multiple times")
        if len(langtable) > 0 and len(langtable[0]['options']) != 1:
            raise errors.ParseError("lang key found with improper number of options")

        if len(langtable) > 0:
            lang = langtable[0]['options'][0]
        else:
            lang = "en_US"

        retval = "lang %s\n" % lang

        langstable = self.getKeys('langs')
        
        if len(langstable) > 1:
            raise errors.ParseError("langs key found multiple times")
        if len(langstable) > 0 and not len(langstable[0]['options']) > 0:
            raise errors.ParseError("langs key found with improper number of options")

        if len(langstable) > 0:
            tmp = ' '.join(langstable[0]['options'])
            langs = "--default %s %s" % (lang, tmp)
        else:
            langs = "--default %s %s" % (lang, lang)

        retval = "%slangsupport %s\n\n" % (retval, langs)
        return retval
        
    def firewall(self):
        firewalltable = self.checkKey(1, 1000, 'firewall')
        firewallstatus = self.checkKey(0, 0, 'enable', 'nofirewall')

        ret = "firewall --medium --ssh --dhcp --port=afs3-callback:tcp,afs3-callback:udp,afs3-errors:tcp,afs3-errors:udp\n"

        if firewallstatus != None:
            ret = "firewall --disabled\n"
        elif firewalltable != None:
            ret = "firewall %s\n" % " ".join(firewalltable)

        return ret

    def inputdevs(self):
        baseInput = baseRealmLinuxKickstart.inputdevs(self)
        mouseargs = self.checkKey(1, 4, 'mouse')

        if mouseargs != None:
            retval = "mouse " + " ".join(mouseargs) + "\n"
        else:
            retval = "mouse --emulthree genericps/2\n"

        retval = "%s%s\n" % (baseInput, retval)

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

    def selinux(self):
        # We revert the SELinux default for 4
        seloptions = self.checkKey(1, 1, 'selinux')
        if seloptions == None: 
            return ''
        else: 
            return "selinux %s\n" % seloptions[0]

    def packages(self):
        # Do the packages section of the KS
        packagetable = self.getKeys('package')

        if len(packagetable) == 0:
            return "%packages\n@ NCSU Realm Kit Workstation\n"
        else:
            retval = "%packages\n"
            for package in packagetable:
                tmp = ' '.join(package['options'])
                retval = "%s%s\n" % (retval, tmp)

            return retval

    def authConfig(self):
        return """
auth --useshadow --enablemd5 --enablehesiod --hesiodlhs .NS --hesiodrhs .EOS.NCSU.EDU --enablekrb5 --krb5realm EOS.NCSU.EDU --krb5kdc kerberos-1.ncsu.edu:88,kerberos-2.ncsu.edu:88,kerberos-3.ncsu.edu:88,kerberos-4.ncsu.edu:88,kerberos-5.ncsu.edu:88,kerberos-6.ncsu.edu:88 --krb5adminserver kerberos-master.ncsu.edu:749
"""

    def runUpdates(self):
        return """
# Run Up2Date
chvt 3
/usr/sbin/up2date --nox -u up2date
/usr/sbin/up2date --nox -u
chvt 1
""" 

