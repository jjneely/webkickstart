#!/usr/bin/python
#
# testconfig.py
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

sys.path.insert(0, "../")

from webKickstart import configtools

log = logging.getLogger('webks')
print "__file__ = %s" % __file__

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.cfgdir = os.path.join(os.path.dirname(__file__), 'testconfig/')
        self.cfg = configtools.Configuration(self.cfgdir)
        log.debug("Config dir: %s" % self.cfgdir)
    
    def test1(self):
        # In our test config file:
        self.assertEqual(self.cfg.logfile, '-')

        # Pulling from the built in defaults:
        self.assertEqual(int(self.cfg.case_sensitivity), 0)

    def testReload(self):
        self.cfg.reload()
        self.test1()

    def testFailures(self):
        # Something Random
        def callBadConfigVar():
            baz = self.cfg.foobar

        self.assertRaises(AttributeError, callBadConfigVar)

    def testVariableAssignment(self):
        foobar = "foobar"

        self.cfg.log_level = foobar
        self.assertEqual(self.cfg.log_level, foobar)
        self.cfg.log_levelbob = foobar
        self.assertEqual(self.cfg.log_levelbob, foobar)

    def testDefaultConfig(self):
        self.assert_(self.cfg.isTrue('collision'))

if __name__ == '__main__':
    unittest.main()

