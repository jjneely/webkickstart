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
        """Merge a table from a solarisConfig into the current table."""
        
        clearpartinfo = 1
        # part information is multiple keys...
        # and package?
        for rec in t:
            if rec['key'] == 'part' and clearpartinfo:
                clearpartinfo = 0
                for rec2 in self.table:
                    if rec2['key'] == 'part':
                        self.table.remove(rec2)
            
            for rec2 in self.table:
                if rec['key'] == rec2['key'] and rec['enable'] == rec2['enable'] and rec['key'] != 'part':
                    self.table.remove(rec2)
            
            self.table.append(rec)
        
            
    def makeKS(self):
        """Return a string containing a RHL kickstart."""
        
        return ""
        
        
    
