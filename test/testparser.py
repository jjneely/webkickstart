#!/usr/bin/python
#
# testparser.py
# Copyright (C) 2007 NC State University
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
from webKickstart.metaparser import MetaParser

log = logging.getLogger('webks')

class TestMetaParser(unittest.TestCase):

    def getFile(self, test):
        return os.path.join(self.cfg.hosts, test)

    def setUp(self):
        if configtools.config == None:
            log.debug("Doing configuration bits...")
            self.cfgdir = os.path.join(os.path.dirname(__file__),
                                       'testconfig/')
            configtools.config = configtools.Configuration(self.cfgdir)

        self.cfg = configtools.config

        self.p1 = MetaParser(self.getFile('meta1'))
        self.p2 = MetaParser(self.getFile('meta2'))
        self.p3 = MetaParser(self.getFile('meta3'))

    def testEquality(self):
        self.assert_(self.p1 != self.p2)
        self.assert_(self.p2 == self.p2)

    def testIsKickstart(self):
        self.assert_(not self.p1.isKickstart())
        self.assert_(    self.p3.isKickstart())

    def testGetCommands(self):
        self.assert_(self.p1.filecommands == ['foo bar', 'bar baz'])
        self.assert_(self.p2.filecommands == ['owner foobar@ncsu.edu',
                                              'use meta2.5'])

        cmd = '\n'.join(self.p1.filecommands)
        self.assert_(self.p1.getCommands() == cmd)

    def testPosts(self):
        posts1 = ['%post\n\n# Post Script\n\n']
        posts2 = ['%post --interpreter /usr/bin/python\n\nprint "Hello World"\n\n', '%post\n\n# Post Script\n\n    date > /.install-date\n']
        
        self.assertEquals(self.p1.getPosts(), posts1)
        self.assertEquals(self.p2.getPosts(), posts2)

    def testVersion(self):
        self.assertNotEqual(configtools.config, None)
        log.debug("hosts = " + configtools.config.hosts)
        self.assert_(self.p1.getVersion(profileKey='foo', includeKey='use') \
                     == 'bar')
        self.assert_(self.p2.getVersion(profileKey='foo', includeKey='use') \
                     == 'sue')


if __name__ == '__main__':
    unittest.main()

