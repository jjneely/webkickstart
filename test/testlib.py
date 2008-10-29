#!/usr/bin/python
#
# testlib.py
# Copyright (C) 2007, 2008 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
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

import os
import sys
import os.path
import unittest
import logging

from webKickstart import configtools
from webKickstart import libwebks

log = logging.getLogger('webks')

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.cfgdir = os.path.join(os.path.dirname(__file__), 'testconfig/')
        log.debug("Config dir: %s" % self.cfgdir)
    
        self.lib = libwebks.LibWebKickstart(self.cfgdir)

    def testFirst(self):
        vars = self.lib.getKeys('anduril.unity.ncsu.edu')
        self.assertTrue(vars.has_key('printer'))
        self.assertEquals(vars['printer'].verbatim(), 'hlb-212-1')

    def testSecond(self):
        vars = self.lib.getKey('foghorn.unity.ncsu.edu', 'package')
        self.assertEquals('@ Realm Linux Server', vars[0])
        self.assertEquals('@ development-tools', vars[1])
        self.assertEquals('@ realmlinux-vmware', vars[2])


if __name__ == '__main__':
    unittest.main()

