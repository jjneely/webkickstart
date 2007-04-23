#!/usr/bin/python
#
# centos5.py - A webKickstart module to handle changes needed from
#              RHEL 5 to CentOS 5 Kickstart generation.
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

class Kickstart(baseRealmLinuxKickstart):

    def __init__(self, url, cfg, sc=None):
        baseRealmLinuxKickstart.__init__(self, url, cfg, sc)

        self.buildOrder.remove(self.installationNumber)
        self.buildOrder.remove(self.RHN)

