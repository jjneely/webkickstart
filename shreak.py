#!/usr/bin/python
#
# shreak.py -- class to generate kickstart from solars config for rk9
#
# Elliot Peele <elliot@bentlogic.net>
# Copyright 2003 NC State University
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

"""This module contains the class used to generate a RK9 kickstart."""

import string
import psycho

class shreak(psycho.psycho):
    version = "9"

    def partition(self):
        # Return partition information
        safepart = self.getKeys('enable', 'safepartition')
                                                                                
        if len(safepart) > 0:
            retval = "zerombr yes\nclearpart --linux\n"
        else:
            retval = "zerombr yes\nclearpart --all\n"
                                                                                
        parttable = self.getKeys('part')
        # We are just going to take what's in the cfg file and go with it
        if len(parttable) == 0:
            parts = """
part / --size 4072
part swap --recommended
part /boot --size 75
part /tmp --size 256 --grow
part /var --size 390
part /var/cache --size 512
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
                                                                                
        retval = "%s%s\n" % (retval, parts)
        return retval
