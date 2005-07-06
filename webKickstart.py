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


    def getKS(self, host, debug=0, collision_detection=0):
        # Figure out the file name to look for, parse it and see what we get.
        # We return a tuple (errorcode, sting) If error code is non-zero
        # the sting will have a description of the error that occured.
        
        addr = socket.gethostbyaddr(host)
        # We look for the A record from DNS...not a CNAME
        filename = addr[0]

        # Get the value for collision_detection
        collision_detection = collision_detection and self.cfg.enable_config_collision_detection

        try:        
            scList = self.findFile(filename)

            if len(scList) > 1:
                s = '# Error: Multiple Web-Kickstart config files found:<br>\n'
                for line in sc:
                    s += '#\t' + line + '\n'
                return (1, s)

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
        """Return a list of absolute paths that match the givein
           filename.  Ie, /foo/bar and /baz/bar when fn="bar"
        """

        ret = []

        try:
            files, dirs = self.getFilesAndDirs(cd)
        except OSError, e:
            s = str(e) + "\nDir: " + cd
            raise OSError(s)

        for f in files:
            if os.path.basename(f) == fn:
                ret.append(solarisConfig(f))

        for d in dirs:
            ret.extend(self.findFile(fn, d))

        return ret

    
    def checkConfigHostnames(self):
        """
        Check for config files that don't resolve in dns any longer.
        """
        list = self.__checkConfigHostnamesHelper(dir="./configs")
        if len(list) == 0:
            s = "No configs found that don't resolve in dns."
        else:
            s = 'The following configs no longer resolve in dns:\n\n'
            for config in list:
                s += '\t%s\n' % config
        return (1, s)

    
    def __checkConfigHostnamesHelper(self, dir, configs=[]):
        list = os.listdir(dir)
        for file in list:
            # Make sure host is still in dns
            try: socket.gethostbyname(file)
            
            # Host that matches config no longer in dns
            except socket.gaierror:
                # Make sure file looks like a hostname
                # (don't want include files)
                if len(file.split('.')) >= 3:
                    configs.append('/'.join([dir, file]))

        # iterate of the rest of the subdirectories
        for d in self.getDirs(list, dir):
            self.__checkConfigHostnamesHelper(d, configs)
            
        return configs                    


    def getFilesAndDirs(self, path):
        # Split up a directory listing of files and directories
        dirs = []
        files = []
        dir = os.listdir(os.path.abspath(path))
        for node in dir:
            apath = os.path.join(path, node)
            if os.path.isdir(apath):
                # isdir() does the right thing if its passed a symlink
                dirs.append(apath)
            elif os.path.isfile(apath):
                files.append(apath)

        return files, dirs

