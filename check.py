#!/usr/bin/python
#
# check.py -- check that va
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

from versionMap import versionMap
from solarisConfig import solarisConfig

import getopt
import sys

def help():
    print """
check.py -- Written by Jack Neely <jjneely@pams.ncsu.edu>
This utility will check the validity of your jump start files for the
Linux Realm Kit.

Usage: check.py [options] <jump start file>

Options:
    -h        | --help          Print this message
    -o <file> | --output <file> Save Kickstart to this file
    -u <URL>  | --url <URL>     URL to grab kickstart at for reinstalls
"""


def main():

    args = sys.argv[1:]

    try:
        optlist, files = getopt.getopt(args, 'ho:', ['help', 'output='])
    except getopt.error:
        help()
        sys.exit(1)

    # file name to save kickstart
    save = None
    # url for reinstall
    url = "http://web-kickstart.linux.ncsu.edu/ks.py"
    
    if len(files) != 1:
        print "I need exactly one file to check."
        help()
        sys.exit(2)

    for o, a in optlist:
        if o in ('--url', '-u'):
            url = a
        if o in ('--help', '-h'):
            help()
            sys.exit(0)
        if o in ('--output', '-o'):
            save = a

    try:
        sc = solarisConfig(files[0])
    except IOError:
        print "Could not read from file " + files[0]
        sys.exit(3)

    try:
        version = sc.getVersion()
        generator = versionMap[version](url, sc)
        ks = generator.makeKS()
    except ParseError, e:
        print "A parse error occured.  The error is:"
        print e.value
        sys.exit(3)

    print "Jump start config file looks proper for configuring a Linux Kickstart."

    if save != None:
        try:
            fd = open(save, "w")
        except IOError:
            print "Error writing saved kickstart to " + save
            sys.exit(4)

        fd.write(ks)
        fd.close()

        print "Kickstart saved as " + save
        

if __name__ == "__main__":
    main()
