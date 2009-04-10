#!/usr/bin/python
#
# webKickstart.py -- finds solaris config file or ks and builds string
#                    to send out apache
#
# Copyright 2002-2008 NC State University
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
from generator import Generator
from errors import *
import configtools

import socket
import traceback
import logging
import stat
import sys
import os
import os.path

log = logging.getLogger("webks")

# Cache constructs
mcCache = {}
mcCacheRoot = ""

class webKickstart(object):

    def __init__(self, url, headers, configDir=None):
        self.__debug = False
        # set up url from reinstalls
        self.url = url
        # client's headers
        self.headers = headers

        if configtools.config == None:
            self.cfg = configtools.Configuration(configDir)
            configtools.config = self.cfg
        else:
            self.cfg = configtools.config

    def __headerCheck(self, fqdn):
        # check for anaconda
        if self.headers.has_key("X-RHN-Provisioning-MAC-0"):
            # continue through...we *know* this is anaconda
            # only present in version >= FC1
            return True
        # This handles anaconda before Fedora which includes RHEL 3
        elif len(self.headers) > 1:
            # Bad
            return False
        elif not self.headers.has_key('Host'):
            # More bad
            return False

        return False

    def setDebug(self, bool):
        "Turn on debug mode, useful for kickstart preview."
        self.__debug = bool

    def __getKS(self, host):
        # Figure out the file name to look for, parse it and see what we get.
        # We return a tuple (errorcode, sting) If error code is non-zero
        # the sting will have a description of the error that occured.
        
        addr = socket.gethostbyaddr(host)
        # We look for the A record from DNS...not a CNAME
        filename = addr[0]

        # Security check
        if not self.__debug and self.cfg.isTrue('security') and not \
                self.__headerCheck(filename):
            log.warning("Requesting client is not Anaconda.")
            return (2, "# You do not appear to be Anaconda.")
        
        mcList = self.findMC(filename)

        if len(mcList) > 1 and self.cfg.isTrue('collision'):
            # if collision_detection is on then bitch
            # otherwise we just want the first hit
            return self.__collisionMessage(mcList)

        if len(mcList) == 0:
            mc = None
        else:
            mc = mcList[0]

        if mc != None:
            if mc.isKickstart():
                log.info("Returning pre-defined kickstart for %s." % filename)
                return (0, mc.getFile())
            
            version = mc.getVersion(self.cfg.profile_key, self.cfg.include_key)
            genny = Generator(version, mc, self.__debug)
        else:
            # disable the default, no-config file, generic kickstart
            if self.cfg.isTrue('generic_ks'):
                genny = Generator('default', mc, self.__debug)
            else:
                log.info("No config file for host " + filename)
                return (1, "# No config file for host " + filename)
                
        log.info("Generating kickstart for %s." % filename)    
        retval = genny.makeKickstart(filename)
        return (0, retval)
        

    def getKS(self, host):
        # Wrapper for error checking/handling
        try:
            return self.__getKS(host)
    
        except WebKickstartError, e:
            s = "An error occured while Web-Kickstart was running.\n"
            s = "%sThe error is:\n%s" % (s, str(e))

            text = ""
            for line in s.split('\n'):
                text = "%s# %s\n" % (text, line)

            log.warning(text)

            return (42, text)
            
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
        

    def findMC(self, fqdn):
        global mcCache, mcCacheRoot
        key = fqdn.lower()
        if self.cfg.hosts == mcCacheRoot and key in mcCache:
            flag = True
            for file in mcCache[key]:
                flag = flag and os.path.exists(file)
            if flag:
                log.debug("Cache Hit: %s" % str(mcCache[key]))
                return [ MetaParser(f) for f in mcCache[key] ]

        log.debug("Cache MISS: %s" % key)
        return self.rebuildCache(fqdn)

    def buildCache(self):
        root = self.cfg.hosts
        cache = {}

        def recurse(dir, dict):
            try:
                files, dirs = self.getFilesAndDirs(dir)
            except OSError, e:
                raise AccessError(str(e))

            for f in files:
                key = os.path.basename(f).lower()
                if key in dict:
                    dict[key].append(f)
                else:
                    dict[key] = [f]

            for d in dirs:
                recurse(d, dict)

        global mcCache, mcCacheRoot
        recurse(root, cache)
        mcCacheRoot = root
        mcCache = cache

    def rebuildCache(self, fqdn):
        """Return a list of MetaConfigs that match the givin FQDN while
           rebuilding the assumed old cache objects.  Matches are case
           insensitive."""

        global mcCache, mcCacheRoot
        self.buildCache()
        key = fqdn.lower()
        if key not in mcCache:
            return []
        return [ MetaParser(f) for f in mcCache[key] ]


    
    def collisionDetection(self, host):
        addr = socket.gethostbyaddr(host)
        # We look for the A record from DNS...not a CNAME
        filename = addr[0]
                         
        scList = self.rebuildCache(filename)

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
        list = self.__checkConfigHostnamesHelper(self.cfg.hosts)
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
            if node.startswith('.'):
                continue
            apath = os.path.join(path, node)
            try:
                # stat() follows symlinks
                mode = os.stat(apath).st_mode
            except os.error:
                continue
            if stat.S_ISDIR(mode):
                dirs.append(apath)
            elif stat.S_ISREG(mode):
                files.append(apath)

        return files, dirs

