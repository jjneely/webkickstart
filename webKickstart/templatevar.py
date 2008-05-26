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

# WebKickstart imports
from errors import *

log = logging.getLogger("webks")

class TemplateVar(object):

    def __init__(self, tokens):
        self.table = []
        self.row = 0
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
                msg = "Refusing to add a list of 0 tokens."
                raise ParseError, msg
            self.table.append(tokens)

        elif isinstance(tokens, StringType):
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

