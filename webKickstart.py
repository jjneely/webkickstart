#!/usr/bin/python
#
# webKickstart.py -- finds solaris config file or ks and builds string
#                    to send out apache
#
# Copyright 2002-2005 NC State University
# Written by Jack Neely <slack@quackmaster.net> and
#            Elliot Peele <elliot@bentlogic.net>
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

import config
import errors
import socket
import traceback
import sys
import os
import os.path
import security


class webKickstart:

    url = ""

    def __init__(self, url, headers):
        # set up url from reinstalls
        self.url = url
        # client's headers
        self.headers = headers

        self.cfg = config.webksconf()
        config.cfg = self.cfg
        security.cfg = self.cfg


    def getKS(self, host, debug=0):
        # Figure out the file name to look for, parse it and see what we get.
        # We return a tuple (errorcode, sting) If error code is non-zero
        # the sting will have a description of the error that occured.
        
        addr = socket.gethostbyaddr(host)
        # We look for the A record from DNS...not a CNAME
        filename = addr[0]

        try:
            sc = self.findFile(filename)

            if not debug and sc != None:
                # Security check
                if self.cfg.enable_security and not security.check(self.headers, filename):
                    return (2, "# You do not appear to be Anaconda.")
                
            if sc != None:
                if sc.isKickstart():
                    return (0, sc.getFile())
            
                version = sc.getVersion()
                args = {'url': self.url, 'sc': sc}
                generator = self.cfg.get_obj(version, args)
            else:
                # disable the default, no-config file, generic kickstart
                if self.cfg.enable_generic_ks:
                    args = {'url': self.url, 'sc': sc}
                    generator = self.cfg.get_obj('default', args)
                else:
                    return (1, "# No config file for host " + host)
                
            retval = generator.makeKS()
            del generator
            del sc
            return (0, retval)
        except:
            text = traceback.format_exception(sys.exc_type,
                                              sys.exc_value,
                                              sys.exc_traceback)
            s = "A python exception occured while parsing the JumpStart file.\n"
            s = "%sThe Exception was:\n\n" % s
            for line in text:
                s = s + line

            return (42, s)
        


    def findFile(self, fn, cd="./configs"):
        # Look through dirs to find this file
        #print "Looking for a file in: " + cd
        try:
            list = os.listdir(cd)
        except OSError, e:
            s = str(e) + "\nDir: " + cd
            raise OSError(s)
        if fn in list:
            #print "Found file: " + os.path.join(cd, fn)
            return solarisConfig(os.path.join(cd, fn))
        else:
            retval = None
            dirs = self.getDirs(list, cd)
            for dir in dirs:
                retval = self.findFile(fn, dir)
                if retval != None:
                    return retval
            # So we didn't find in, return None
            return None

        

    def getDirs(self, dirlist, basepath=""):
        # Returns a list of all directories in the directory listing
        # provided.
        dirs = []
        for node in dirlist:
            if os.path.isdir(os.path.join(basepath, node)):
                dirs.append(os.path.join(basepath, node))

        return dirs
