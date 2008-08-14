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
from webKickstart.generator import Generator
from webKickstart.templatevar import TemplateVar

log = logging.getLogger('webks')

class TestTemplateVar(unittest.TestCase):

    def testA(self):
        tokens = ['a', 'b', '1', '2']
        var = TemplateVar(tokens)
        self.assertEqual(var.key(), 'a')
        
        self.assertEqual(var.verbatim(), 'b 1 2')
        self.assertEqual(var.options(), ['b', '1', '2'])
        self.assertEqual(var.len(), 3)

    def testRecords(self):
        tokens = [['a', 'b', '1', '2'],
                  ['a', 'z', 'x', 'c', 'v', 'b'],
                  ['a', '1', '2', '3']]

        var = TemplateVar(tokens[0])
        var.append(tokens[1])
        var.append(tokens[2])

        self.assertEqual(var.verbatim(), 'b 1 2')
    
        i = 0
        for element in var:
            #log.debug(i)
            self.assertEqual(element.key(), 'a')
            self.assertEqual(element.verbatim(), ' '.join(tokens[i][1:]))
            i = i + 1

class TestGenerator(unittest.TestCase):

    def getFile(self, test):
        return os.path.join(self.cfg.hosts, test)

    def setUp(self):
        self.cfgdir = os.path.join(os.path.dirname(__file__), 'testconfig/')
        self.cfg = configtools.Configuration(self.cfgdir)
        configtools.config = self.cfg
        log.debug("Config dir: %s" % self.cfgdir)

    def testCreate(self):
        gen = Generator('rl5')

    def testGenny(self):
        mc = MetaParser(self.getFile('genny1'))
        gen = Generator('rl5', mc)

        rows = ["nox",
                "adminusers jjneely tkl bob",
                "localcluster pams",
                "remotecluster pams",
                "nofirewall" ]
        
        self.assertTrue(gen.variables.has_key('enable'))

        stuff = gen.variables['enable']
        self.assertEqual(stuff.records(), 5)

        i = 0
        for record in stuff:
            self.assertEqual(record.verbatim(), rows[i])
            i = i + 1


if __name__ == '__main__':
    unittest.main()

