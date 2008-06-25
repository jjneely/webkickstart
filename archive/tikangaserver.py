#!/usr/bin/python
#
# tikangaserver.py - Difference from Tikanga Client
#
# Copyright 2007 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
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

import re

class Kickstart(baseRealmLinuxKickstart):

    def __init__(self, url, cfg, sc=None):
        baseRealmLinuxKickstart.__init__(self, url, cfg, sc)

    # XXX: Server and Client are only different in available packages.
    # Should we be offering differen default packages sets besides
    # something workstation-ish?
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
                       #'eclipse',
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
                       #'workstation',
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

