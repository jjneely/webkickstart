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

from webKickstart.webks import webKickstart
from webKickstart import configtools
from webKickstart.metaparser import MetaParser
from webKickstart.generator import Generator

log = logging.getLogger('webks')

class TestGenerator(object):

    def makeKS(self, fqdn, conf):
        wks = webKickstart("url/", {}, conf)
        wks.setDebug(True)

        t = wks.getKS(fqdn)
        print t[1]
        return t[0]


def main():
    parser = optparse.OptionParser("%%prog %s [options] hostname" % \
                                   sys.argv[0])
    parser.add_option("-C", "--configdir", action="store", type="string",
           dest="configdir", default=None,
           help="Configuration directory. [/etc/webkickstart]")

    (opts, args) = parser.parse_args(sys.argv)

    if len(args) != 2:
        parser.print_help()
        sys.exit()

    fqdn = args[1]

    t = TestGenerator()
    t.makeKS(fqdn, opts.configdir)


if __name__ == '__main__':
    main()

