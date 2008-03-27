#!/usr/bin/python
#
# webKickstart.py -- finds solaris config file or ks and builds string
#                    to send out apache
#
# Copyright 2002-2005 NC State University
# Written by Jack Neely <jjneely@pams.ncsu.edu> and
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

from metaparser import MetaParser
from errors import *
import configtools
import security

import socket
import traceback
import logging
import sys
import os
import os.path

log = logging.getLogger("webks")

class webKickstart:

    url = ""

    def __init__(self, url, headers):
        # set up url from reinstalls
        self.url = url
        # client's headers
        self.headers = headers

        self.cfg = configtools.config
        #config.cfg = self.cfg
        security.cfg = self.cfg


    def __getKS(self, host, debug=0):
        # Figure out the file name to look for, parse it and see what we get.
        # We return a tuple (errorcode, sting) If error code is non-zero
        # the sting will have a description of the error that occured.
        
        addr = socket.gethostbyaddr(host)
        # We look for the A record from DNS...not a CNAME
        filename = addr[0]

        # Get the value for collision_detection
        collision_detection = self.cfg.enable_config_collision_detection

        scList = self.findFile(filename, self.cfg.jumpstarts)

        if len(scList) > 1 and collision_detection:
            # if collision_detection is on then bitch
            # otherwise we just want the first hit
            return self.__collisionMessage(scList)

        if len(scList) == 0:
            sc = None
        else:
            sc = scList[0]

        if not debug and sc != None:
            # Security check
            if ( self.cfg.enable_security and 
                 not security.check(self.headers, filename) ):
                return (2, "# You do not appear to be Anaconda.")
                
        if sc != None:
            if sc.isKickstart():
                log.info("Returning pre-defined kickstart for %s." % filename)
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
                log.info("No config file for host " + filename)
                return (1, "# No config file for host " + filename)
                
        log.info("Generating kickstart for %s." % filename)    
        retval = generator.makeKS()
        return (0, retval)
        

    def getKS(self, host, debug=0):
        # Wrapper for error checking/handling
        try:
            return self.__getKS(host, debug)
    
        except WebKickstartError, e:
            s = "# An error occured while Web-Kickstart was running.\n"
            s = "%s# The error is: %s" % (s, str(e))

            log.warning(s)

            return (42, s)
            
        except:
            text = traceback.format_exception(sys.exc_type,
                                              sys.exc_value,
                                              sys.exc_traceback)
            s = "# An unhandled python exception occured in Web-Kickstart.\n"
            s = "%s# The Exception was:\n\n" % s

            # We need to comment everything out.  text is a list and each
            # element may contain more than one line of traceback.
            text = '\n'.join(text)
            for line in text.split('\n'):
                s = "%s# %s\n" % (s, line)

            log.error(s)

            return (42, s)
        

    def findFile(self, fn, cd="./configs"):
        """Return a list of MetaParserss that match the givein
           filename.  Ie, /foo/bar and /baz/bar when fn="bar".  This
           is case insensitive as is DNS.
        """

        ret = []
        fn = fn.lower()

        try:
            files, dirs = self.getFilesAndDirs(cd)
        except OSError, e:
            raise AccessError(str(e))

        for f in files:
            if os.path.basename(f).lower() == fn:
                ret.append(MetaParser(f))

        for d in dirs:
            ret.extend(self.findFile(fn, d))

        return ret

    
    def collisionDetection(self, host):
        addr = socket.gethostbyaddr(host)
        # We look for the A record from DNS...not a CNAME
        filename = addr[0]
                         
        scList = self.findFile(filename, self.cfg.jumpstarts)

        if len(scList) > 1:
            return self.__collisionMessage(scList)

        s = "No collisions found for %s" % filename
        return (1, s)

        
    def __collisionMessage(self, scList):
        s = 'Multiple Web-Kickstart config files found:\n'
        for sc in scList:
            s += '\t%s\n' % str(sc)
            
        return (1, s)

        
    def checkConfigHostnames(self):
        """
        Check for config files that don't resolve in dns any longer.
        """
        list = self.__checkConfigHostnamesHelper(self.cfg.jumpstarts)
        if len(list) == 0:
            s = "No config files found that don't resolve in dns."
        else:
            s = 'The following configs no longer resolve in dns:\n\n'
            for config in list:
                s += '\t%s\n' % config
        return (1, s)

    
    def __checkConfigHostnamesHelper(self, dir):
        configs = []
        files, dirs = self.getFilesAndDirs(dir)
        for file in files:
            # We always get an absoulte file name
            host = os.path.basename(file)
            # Make sure host is still in dns
            try: 
                socket.gethostbyname(host)
            
            # Host that matches config no longer in dns
            except socket.gaierror:
                # Make sure file looks like a hostname
                # (don't want include files)
                if len(host.split('.')) >= 3:
                    configs.append(file)

        # iterate of the rest of the subdirectories
        for d in dirs:
            configs.extend(self.__checkConfigHostnamesHelper(d))
            
        return configs                    


    def getFilesAndDirs(self, path):
        # Split up a directory listing of files and directories
        dirs = []
        files = []

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        dir = os.listdir(path)
        for node in dir:
            apath = os.path.join(path, node)
            if os.path.isdir(apath):
                # isdir() does the right thing if its passed a symlink
                dirs.append(apath)
            elif os.path.isfile(apath):
                files.append(apath)

        return files, dirs

