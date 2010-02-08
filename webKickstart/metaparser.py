#!/usr/bin/python
#
# metaparser.py -- tools for parsing the host config files
#
# Copyright 2002-2006 NC State University
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

import logging
import string
import shlex
import cStringIO
import os

import errors
import configtools

log = logging.getLogger("webks")

# Constants for the config file FSM parser
scriptTypes = ['%packages', '%post', '%pre', '%traceback', '%include']

STATE_COMMANDS = 0
STATE_SCRIPT = 1
STATE_INCLUDE = 2

class MetaParser(object):
    """This class has tools and functions for parsing a host config file.
       We can recognize if this is a normal kickstart instead.  This class is
       ment to be used by a factory class to produce a Red Hat Kickstart."""
    
    def __init__(self, filename):
        self.filename = filename
        self.filedata = ""
        self.filecommands = []
        self.fileposts = []
        self.parsings = None

        log.info("Reading meta config: %s" % self.getFileName())

        file = open(self.getFileName())
        
        self.filedata = file.read()
        file.close()
        lines = string.split(self.filedata, '\n')
        self.filecommands, self.fileposts = self.__FSMParser(lines)
        
   
    def __str__(self):
        return "Web-Kickstart Config: %s " % self.getFileName()


    def __eq__(self, sc):
        if sc is None: return False
        return self.getFileName() == sc.getFileName()


    def __ne__(self, sc):
        if sc is None: return True
        return self.getFileName() != sc.getFileName()
    

    def __isScriptHeader(self, line):
        """FSM helper.  Test line for a %-command."""

        if not line.startswith('%'): 
            return False

        for section in scriptTypes:
            if line.startswith(section):
                return True

        err = 'Config contains invalid %%-command on line:\n   %s' % line
        raise errors.ParseError(err)


    def __FSMParser(self, lines):
        """Parse the config file into commands and a series of scripts."""

        commands = []
        scripts = []
        tmp = []

        state = STATE_COMMANDS
        for line in lines:
            isHdr = self.__isScriptHeader(line)

            if state == STATE_COMMANDS:
                if isHdr and line.startswith('%include'):
                    scripts.append([line])
                    state = STATE_INCLUDE
                elif isHdr:
                    tmp = [line]
                    state = STATE_SCRIPT
                else:
                    stripped = line.strip()
                    if stripped != "":
                        commands.append(stripped)

            elif state == STATE_SCRIPT:
                if isHdr and line.startswith('%include'):
                    scripts.append([line])
                    state = STATE_INCLUDE
                elif isHdr:
                    scripts.append(tmp)
                    tmp = [line]
                else:
                    tmp.append(line)

            elif state == STATE_INCLUDE:
                if isHdr and line.startswith('%include'):
                    scripts.append([line])
                elif isHdr:
                    tmp = [line]
                    state = STATE_SCRIPT
                else:
                    # eat the empty space
                    pass
            else:
                err = "Unknown state while parsing config file."
                raise errors.ParseError(err)

        if len(tmp) > 0:
            scripts.append(tmp)

        return commands, scripts


    def isKickstart(self):
        """Return true if this config file appears to be a kickstart"""
        
        ksReqs = ['auth', 'keyboard', 'lang', 'bootloader', 
                  'rootpw', 'timezone']
        coms = self.getListOfKeys()
        
        for key in ksReqs:
            if key not in coms:
                # this is not a ks
                return False

        return True
        
        
    def getLine(self, num):
        """Returns a list of parsed tokens from line number num in the
           commands section of the config file."""
        
        def wraplex(l, source):
            try:
                return l.get_token()
            except Exception, e:
                msg = "Error Parsing:\n"
                msg = "%s%s\n\n" % (msg, source.getvalue())
                msg = "%sError message: %s" % (msg, str(e))
                raise errors.ParseError, msg

        if num >= len(self.filecommands):
            return None
        
        s = cStringIO.StringIO(self.filecommands[num])
        lex = shlex.shlex(s)
        lex.wordchars = lex.wordchars + "-./=$:@,+"
        ops = []
        
        t = wraplex(lex, s)
        while not t == "":
            ops.append(self.__cleanToken(t))
            t = wraplex(lex, s)
        
        return ops
        
        
    def __cleanToken(self, token):
        """shlex does a nice job but leaves quotes around tokens if quotes are
           used.  So lets strip off the quotes and return a cleaned token."""
         
        if len(token) == 0:
            return token
        if (token[0] == '\'' or token[0] == '"') and (token[0] == token[-1]):
            return token[1:-1]
        else:
            return token
        
        
    def getCommands(self):
        """Returns a string of the commands section of the file."""
        
        return '\n'.join(self.filecommands)
        
        
    def getPosts(self):
        """Returns a list of a % sections in the config file."""
        # This is an API change 11/9/2007
        #    used to join together the lines into one string

        scripts = []
        for post in self.fileposts:
            scripts.append('\n'.join(post))

        # We reverse the order of %posts in the generator.  Why?  We want
        # MetaConfigs higher on the tree to override those that are on 
        # lower nodes/children.  However, %posts from the same MC should
        # be next to each other and in the same order.
        scripts.reverse()

        return scripts
        
        
    def getFile(self):
        """Return a string of the entire config file."""
        
        return self.filedata
        
    
    def getFileName(self):
        if os.path.isabs(self.filename):
            if os.access(self.filename, os.R_OK):
                return self.filename
        else:
            filename = os.path.join(configtools.config.hosts, self.filename)
            if os.access(filename, os.R_OK):
                return filename

            # XXX: Support legacy configs/ directory
            if self.filename.startswith("configs/"):
                filename = os.path.join(configtools.config.hosts, 
                                        self.filename[8:])
                if os.access(filename, os.R_OK):
                    return filename

        raise errors.AccessError("Cannot find config file: %s" % self.filename)

        
    def getListOfKeys(self):
        """Return a list of all keywords used in config file."""

        return [ l[0] for l in self.parseCommands() ]
    
    
    def parseCommands(self):
        """Returns a list of lists of all parsed commands/options."""
        
        if self.parsings != None:
            return self.parsings
        
        ret = []
        c = 0
        line = self.getLine(c)
        while line != None:
            if line != []:
                ret.append(line)
            c = c + 1
            line = self.getLine(c)
        
        self.parsings = ret
        return ret
        
        
    def getVersion(self, profileKey='version', includeKey='use'):
        """Returns the option ofter the 'version' key."""
        
        if self.isKickstart():
            return None
        
        version = self.__parseOutVersion(self, profileKey, includeKey)
        if version is None:
            raise errors.ParseError("'%s' key is missing and required" \
                                    % profileKey)
        
        return version


    def __parseOutVersion(self, sc, profileKey, includeKey, sclist=None):
        """Parse version out of included files"""

        # Gah...default argument values are only evaluated once so if I
        # use a list (mutable) and then do things to it...i will always
        # get the modified list passed in to the initial function call.
        
        if sclist == None:
            sclist = []

        #log.debug("In __parseOutVersion()")
        #log.debug("  sclist = %s" % str(sclist))
        
        # Gaurd against infinite recursion
        fn = sc.getFileName()
        if fn in sclist:
            log.warning("Infinite recursion detected: %s" % fn)
            return None
        sclist.append(fn)

        for rec in sc.parseCommands():
            #log.debug("Parsing for version: key: %s" % rec[0])
            if rec[0] == profileKey:
                if len(rec) != 2:
                    errmsg = "'%s' key must have one argument." % profileKey
                    raise errors.ParseError(errmsg)
                else:
                    return rec[1]

        for rec in sc.parseCommands():
            if rec[0] == includeKey:
                if len(rec) != 2:
                    errmsg = "'%s' key must have one argument." % includeKey
                    raise errors.ParseError(errmsg)
 
                newsc = MetaParser(rec[1])
                v = self.__parseOutVersion(newsc, profileKey, includeKey,
                                           sclist)
                if v is not None:
                    return v

        return None

