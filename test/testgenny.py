#!/usr/bin/python
#
# testgenny.py
# Copyright (C) 2008 NC State University
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
from webKickstart.generator import Generator, TemplateVar

log = logging.getLogger('webks')

class TestTemplateVar(unittest.TestCase):

    def testA(self):
        tokens = ['a', 'b', '1', '2']
        var = TemplateVar(tokens)
        self.assertEqual(var.key(), 'a')
        
        self.assertEqual(var.verbatim(), 'a b 1 2')
        self.assertEqual(var.options(), ['b', '1', '2'])
        self.assertEqual(var.len(), 3)

    def testRecords(self):
        tokens = [['a', 'b', '1', '2'],
                  ['z', 'x', 'c', 'v', 'b'],
                  ['1', '2', '3']]

        var = TemplateVar(tokens[0])
        var.append(tokens[1])
        var.append(tokens[2])

        self.assertEqual(var.verbatim(), 'a b 1 2')
    
        i = 0
        for element in var:
            log.debug(i)
            self.assertEqual(element.key(), tokens[i][0])
            self.assertEqual(element.verbatim(), ' '.join(tokens[i]))
            i = i + 1

class TestGenerator(unittest.TestCase):

    def getFile(self, test):
        return os.path.join(os.getcwd(), self.testfiles, test)

    def setUp(self):
        if configtools.config == None:
            log.debug("Doing configuration bits...")
            self.cfgdir = os.path.join(os.path.dirname(__file__),
                                       'testconfig/')
            configtools.config = configtools.Configuration(self.cfgdir)

        self.cfg = configtools.config

        self.testfiles = os.path.join(os.path.dirname(__file__), 'testdata/')
        self.cfg.hosts = self.testfiles

    def testCreate(self):
        gen = Generator('profile')

    def testGenny(self):
        mc = MetaParser(self.getFile('genny1'))
        gen = Generator('profile', mc)

        rows = ["enable nox",
                "enable adminusers jjneely tkl bob"]
        
        self.assertTrue(gen.variables.has_key('enable'))

        stuff = gen.variables['enable']
        self.assertEqual(stuff.records(), 2)

        print stuff
        i = 0
        for record in stuff:
            print record
            self.assertEqual(record.verbatim(), rows[i])
            i = i + 1


if __name__ == '__main__':
    unittest.main()

