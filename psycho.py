#!/usr/bin/python
#
# versionMap.py -- Maps version numbers to kickstart generator classes
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

"""This module contains the class used to generate a RK8.0 kickstart."""

import baseKickstart

class psycho(baseKickstart.baseKickstart):

    version = "8.0"
        
    def packages(self):
        # Do the packages section of the KS.
        # The default package groups changed in RK8.0 so we overload this
        # function.
        packagetable = self.getKeys('package')

        if len(packagetable) == 0:
            return "%packages\n@ NCSU Realm Kit Workstation\n"
        else:
            retval = "%packages\n"
            for package in packagetable:
                tmp = string.join(package['options'])
                retval = "%s%s\n" % (retval, tmp)

            return retval
