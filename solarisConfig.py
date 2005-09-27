#!/usr/bin/python
#
# solarisConfig.py -- tools for parsing solaris config files
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

import string
import shlex
import cStringIO
import errors

class solarisConfig:
    """This class has tools and functions for parsing a solaris config file.
       We can recognize if this is a normal kickstart instead.  This class is
       ment to be used by a factory class to produce a Red Hat Kickstart."""
    
    filename = ""
    filedata = ""
    filecommands = []
    fileposts = []
    
    parsings = None
    
    def __init__(self, filename):
        file = open(filename)
        # Do we need to handle exception or let them propigate up?
        self.filename = filename
        
        self.filedata = file.read()
        file.close()
        lines = string.split(self.filedata, '\n')
        self.filecommands, self.fileposts = self.__splitFile(lines)
        
   
    def __str__(self):
        return "Web-Kickstart Config: %s " % self.filename


    def __splitFile(self, lines):
        """Separates the file into the first part of commands and the second
           part containing any %post, %pre, %packages, %anything."""
        
        breakpoint = 0
        for line in lines:
            s = string.strip(line)
            if len(s) > 0 and s[0] == "%":
                break
            breakpoint = breakpoint + 1
        
        return lines[0:breakpoint], lines[breakpoint:]
        
        
    def isKickstart(self):
        """Return true if this config file appears to be a kickstart"""
        
        ksReqs = ['auth', 'keyboard', 'lang', 'mouse', 'rootpw', 'timezone']
        coms = self.getListOfKeys()
        
        for key in ksReqs:
            if key not in coms:
                # this is not a ks
                return 0

        return 1
        
        
    def getLine(self, num):
        """Returns a dict containing 'key', 'enable', and 'options' found on this line number.
           This assumes you are looking in the commands section.  Key will be '' if
           line does not contain a key or options.  None will be returned if the
           line number is out of range."""
        
        if num >= len(self.filecommands):
            return None
        
        s = cStringIO.StringIO(self.filecommands[num])
        lex = shlex.shlex(s)
        lex.wordchars = lex.wordchars + "-./=$:@,"
        dict = {}
        ops = []
        
        dict['key'] = self.__cleanToken(lex.get_token())
        if dict['key'] == 'enable':
            dict['enable'] = self.__cleanToken(lex.get_token())
        else:
            dict['enable'] = ''
            
        s2 = lex.get_token()
        while not s2 == "":
            ops.append(self.__cleanToken(s2))
            s2 = lex.get_token()
        dict['options'] = ops
        
        return dict
        
        
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
        
        return string.join(self.filecommands, '\n')
        
        
    def getPost(self):
        """Returns a string of the rest of the file after the '%post'"""
        
        return string.join(self.fileposts, '\n')
        
        
    def getFile(self):
        """Return a string of the entire config file."""
        
        return self.filedata
        
        
    def getListOfKeys(self):
        """Return a list of all keywords used in config file."""

        coms = []
        for i in range(len(self.filecommands)):
            dict = self.getLine(i)
            if dict != None and dict['key'] != '':
                coms.append(dict['key'])    
            
        return coms
    
    
    def parseCommands(self):
        """Returns a list of dicts of all commands and their options."""
        
        if self.parsings != None:
            return self.parsings
        
        ret = []
        c = 0
        line = self.getLine(c)
        while line != None:
            if line['key'] != "":
                ret.append(line)
            c = c + 1
            line = self.getLine(c)
        
        self.parsings = ret
        return ret
        
        
    def getVersion(self):
        """Returns the option ofter the 'version' key."""
        return self.__parseOutVersion(self)


    def __parseOutVersion(self, sc):
        """Parse version out of included files"""
        for rec in sc.parseCommands():
            if rec['key'] == 'version':
                if len(rec['options']) != 1:
                    raise errors.ParseError, "'version' key must have one argument."
                else:
                    return rec['options'][0]

            if rec['key'] == 'use':
                if len(rec['options']) != 1:
                    raise errors.ParseError, "'use' key must have one argument."
                try:
                    v = self.__parseOutVersion(solarisConfig(rec['options'][0]))
                except errors.ParseError, e:
                    # if the included conf file doesn't have a version
                    # we need to keep looking
                    # Also, check which exception was thrown for completeness
                    # XXX: This function needs to be fixed better.
                    if e.value != "'version' key is required.":
                        raise

        if not sc.isKickstart():
            raise errors.ParseError, "'version' key is required."
        else:
            return None

            
