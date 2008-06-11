#!/usr/bin/python
#
# templatevar.py - Define the TemplateVar class
#
# Copyright 2008 NC State University
# Written by Jack Neely <jjneely@pams.ncsu.edu>
#
# SDG
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

# Pythong imports
from types import *
import logging
import re

# WebKickstart imports
from errors import *

log = logging.getLogger("webks")

class TemplateVar(object):

    def __init__(self, tokens, key=None, noKey=False):
        """
        tokens -- A list of strings or a single string that becomes the
           initial value of this TemplateVar Object

        key -- An optional key value to refer to this TemplateVar

        noKey -- Set to True if tokens[0] is not the key, otherwise
           we assume that if tokens is a list the first value is the key
        """

        self.table = []
        self._key = None     # Say my name!
        self.row = 0
        self.regex = {}     # regular expression cache
        self.members = {}   # Extra members that may have been added

        isKeySet = False

        if self._key is None and key is not None and not noKey:
            self._key = key
            isKeySet = True     # Make note if we have already set key

        self.append(tokens, isKeySet=isKeySet, noKey=noKey)

        # For the iterator, we need to know if this is the inital
        # creation/data row.  
        self._flag = 1

    def __iter__(self):
    	return self
    	
    def __str__(self):
        return self.verbatim()

    def __getitem__(self, idx):
        return self.table[self.row][idx]

    def __getattr__(self, name):
        if self.members.has_key(name):
            return self.members[name]
        else:
            raise AttributeError, name

    def __setitem__(self, idx, val):
        raise WebKickstartError, "Refusing to alter values from a metaconfig."
        
    def next(self):
        if self._flag == 1:
            self._flag = 0
        else:
            self.row = self.row + 1

        if self.row >= len(self.table):
            self.reset()
            raise StopIteration

        return self

    def reset(self):
        self.row = 0
    
    def append(self, tokens, isKeySet=True, noKey=False):
        """
        The tokens variable is either a string or a list of strings that
        make a value to assign this 'row' of this TemplateVar.  A single
        string may be a script or test file, while a list may be the parsed
        tokens of a MetaConfig file.

        We assume that the key or the string that identifies this
        TemplateVar is tokens[0] if tokens is a list.  If tokens is a 
        string or noKey is True then we do not look for the key in the
        tokens variable.

        The isKeySet variable helps us not override a previously set
        value for the key.
        """
        if isinstance(tokens, ListType):
            if len(tokens) == 0 and not noKey:
                msg = "Refusing to add a list of 0 tokens to TemplateVar."
                raise ParseError, msg
            if noKey:
                self.table.append(tokens)
            elif len(tokens) > 1:
                self.table.append(tokens[1:])
            else: # len(tokens) == 1 and tokens[0] == key
                self.table.append([])
            if not isKeySet and not noKey:
                self._key = tokens[0]

        elif isinstance(tokens, StringType):
            self.table.append([tokens])

        else:
            msg = "Unsupported token type for TemplateVar class."
            raise WebKickstartError, msg

    def verbatim(self):
        return ' '.join(self.table[self.row])

    def key(self):
        return self._key

    def options(self):
        return self.table[self.row]

    def len(self):
        return len(self.table[self.row])

    def records(self):
        return len(self.table)

    def match(self, regex):
        """Match the provided regex against self.verbatim().
           We return a MatchObject on success, or None on failure.
           This can be used like so for the simple case:

              #if foo.match('bob.*sue')

           using Cheetah synatx
        """

        if not self.regex.has_key(regex):
            self.regex[regex] = re.compile(regex)

        c = self.regex[regex]
        return c.match(self.verbatim())

    def setMember(self, member, value, noKey=False):
        """Sets a member that can be accessed via foo.<member> where
           foo is an instance of TemplateVar.  foo.<member> is assigned
           a value of value which must be a string."""

        # How crazy is this?
        var = TemplateVar(value, key=member, noKey=noKey)
        self.members[member] = var

    def hasMember(self, name):
        return self.members.has_key(name)

