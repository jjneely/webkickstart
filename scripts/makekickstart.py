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
import optparse

from webKickstart import configtools
from webKickstart.metaparser import MetaParser
from webKickstart.generator import Generator

log = logging.getLogger('webks')

class TestGenerator(object):

    def setUp(self, dir=None):
        if configtools.config == None:
            log.debug("Doing configuration bits...")
            if dir is not None:
                self.cfgdir = dir
                if not os.path.isabs(self.cfgdir):
                    self.cfgdir = os.path.abspath(self.cfgdir)
            else:
                self.cfgdir = None

            configtools.config = configtools.Configuration(self.cfgdir)

        self.cfg = configtools.config

    def makeKS(self, filename):
        # Load the config file into a MetaParser object
        mc = MetaParser(filename)

        # Grab out the version/profile string
        version = mc.getVersion(self.cfg.profile_key, self.cfg.include_key)
        log.debug("Found version string: %s" % version)

        # The mod_python bits assume the FQDN matches the basename of the
        # config file.  For generating the file you can aquire the FQDN
        # any way that's useful.
        fqdn = os.path.basename(filename)

        # Create a Generator object
        gen = Generator(version, mc)
        
        # Assumble the kickstart
        print gen.makeKickstart(fqdn)


def main():
    parser = optparse.OptionParser("%%prog %s [options] MetaConfig" % \
                                   sys.argv[0])
    parser.add_option("-C", "--configdir", action="store", type="string",
           dest="configdir", default=None,
           help="Configuration directory. [/etc/webkickstart]")

    (opts, args) = parser.parse_args(sys.argv)

    if len(args) != 2:
        parser.print_help()
        sys.exit()

    filename = args[1]

    t = TestGenerator()
    t.setUp(opts.configdir)
    t.makeKS(filename)


if __name__ == '__main__':
    main()

