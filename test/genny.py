#!/usr/bin/python
#
# genny.py
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
import logging

sys.path.insert(0, "../")

from webKickstart import configtools
from webKickstart.metaparser import MetaParser
from webKickstart.generator import Generator

log = logging.getLogger('webks')

class TestGenerator(object):

    def getFile(self, test):
        return os.path.join(os.getcwd(), self.testfiles, test)

    def setUp(self):
        if configtools.config == None:
            log.debug("Doing configuration bits...")
            self.cfgdir = os.path.join(os.path.dirname(__file__),
                                       'testconfig/')
            if not os.path.isabs(self.cfgdir):
                self.cfgdir = os.path.abspath(self.cfgdir)
            configtools.config = configtools.Configuration(self.cfgdir)

        self.cfg = configtools.config
        log.debug("hosts: %s" %configtools.config.hosts)

    def makeKS(self, profile, filename):
        mc = MetaParser(filename)
        gen = Generator(profile, mc)
        
        print gen.makeKickstart(os.path.basename(filename))

if __name__ == '__main__':
    
    if len(sys.argv) != 3:
        print "Usage: python %s ProfileName Filename" % sys.argv[0]
        sys.exit()

    profile = sys.argv[1]
    filename = sys.argv[2]

    t = TestGenerator()
    t.setUp()
    t.makeKS(profile, filename)

