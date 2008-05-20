#!/usr/bin/python
#
# __init__.py - Handle plugins found in webKickstart.plugins
# Copyright (C) 2008 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
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

import os
import os
import os.path
import logging

# Make the TemplateVar avaiable as plugins will need it
from webKickstart.templatevar import TemplateVar

log = logging.getLogger('webks')

class WebKickstartPlugin(object):

    def __init__(self, variableDict):
        self.variableDict = variableDict

    def addVar(self, tv):
        if not isinstance(tv, TemplateVar):
            raise WekKickstartError, "addVar() requires a TemplateVar argument"

        if self.variableDict.has_key(tv.key()):
            self.variableDict[tv.key()].append(tv.tokens)
        else:
            self.variableDict[tv.key()] = tv

    def run(self):
        """This must return a new dict of variables to use in parsing
           the template."""

        return self.variableDict


def getModules():
    list = []
    modules = {}
    path = os.path.dirname(__file__)

    log.debug("Loading WebKickstart plugins from path: %s" % path)

    files = os.listdir(path)
    for file in files:
        if file.startswith('_'):
            continue
        if file.startswith('.'):
            continue
        if not file.endswith('.py'):
            continue
        list.append(file[:-3])

    for m in list:
        try:
            mod = __import__(m, globals(), locals(), ['webKickstart.plugins'])
        except ImportError, e:
            log.error("Failed to import module: %s" % m)
            continue

        for n, obj in mod.__dict__.items():
            if not type(obj) == type(object):
                continue
            if not issubclass(obj, WebKickstartPlugin):
                continue
            if obj is WebKickstartPlugin:
                continue
            
            modules[m] = obj

    return modules

