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

    def __init__(self, tokens):
        self.table = []
        self.row = 0
        self.regex = {}     # regular expression cache
        self.members = {}   # Extra members that may have been added

        self.append(tokens)

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
    
    def append(self, tokens):
        if isinstance(tokens, ListType):
            if len(tokens) == 0:
                msg = "Refusing to add a list of 0 tokens to TemplateVar."
                raise ParseError, msg
            self.table.append(tokens)

        elif isinstance(tokens, StringType):
            if tokens == "":
                msg = "Refusing to add an empty token to TemplateVar."
                raise ParseError, msg
            self.table.append([tokens])

        else:
            msg = "Unsupported token type for TemplateVar class."
            raise WebKickstartError, msg

    def verbatim(self):
        return ' '.join(self.table[self.row])

    def key(self):
        return self.table[self.row][0]

    def verbatimOptions(self):
        return ' '.join(self.options())

    def options(self):
        return self.table[self.row][1:]

    def len(self):
        return len(self.table[self.row][1:])

    def records(self):
        return len(self.table)

    def match(self, regex):
        """Match the provided regex against self.verbatimOptions().
           We return a MatchObject on success, or None on failure.
           This can be used like so for the simple case:

              #if foo.match('bob.*sue')

           using Cheetah synatx
        """

        if not self.regex.has_key(regex):
            self.regex[regex] = re.compile(regex)

        c = self.regex[regex]
        return c.match(self.verbatimOptions())

    def setMember(self, member, value):
        """Sets a member that can be accessed via foo.<member> where
           foo is an instance of TemplateVar.  foo.<member> is assigned
           a value of value which must be a string."""

        if isinstance(value, StringType):
            tokens = [member, value]
        elif isinstance(value, ListType):
            tokens = [member] + value
        else:
            msg = "setMamber()'s value must be a list of strings or a string."
            raise WebKickstartError, msg

        # How crazy is this?
        var = TemplateVar(tokens)
        self.members[member] = var
        log.debug("Created member of '%s' with: %s" % \
                (self.key(), str(var.table)))

