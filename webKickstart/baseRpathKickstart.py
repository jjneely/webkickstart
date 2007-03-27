#
# baseRpathKickstart.py -- class to generate a kickstart from a solarisConfig
#
# Copyright 2005 NC State University
# Written by Elliot Peele <elliot@bentlogic.net>
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

from baseKickstart import baseKickstart

class baseRpathKickstart(baseKickstart):

    def packages(self):
        if '%packages' in self.extraPost():
            return ""
        elif len(self.getKeys('package')) == 0:
            return '%packages'
        else:
            return baseKickstart.packages(self)

    def printer(self):
        return ''


