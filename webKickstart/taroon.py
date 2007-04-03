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

import nahant

class Kickstart(nahant.Kickstart):

    def audit(self):
        # kill auditd with a big hammer unless anyone really wants to use it
        # The auditd deamon in RHEL 3 is called "audit" in RHEL 4 "auditd"
        # We override for RHEL 3
        audittable = self.getKeys('enable', 'audit')
        if len(audittable) > 1:
            raise errors.ParseError('Multiple audit keys found')
        elif len(audittable) == 1:
            retval = """
# make sure audit is on
chkconfig audit on

"""
        else:
            retval = """
# turn off audit and wax any logs
chkconfig audit off
rm -rf /var/log/audit
rm -rf /var/log/audit.d/*

"""
        return retval            

