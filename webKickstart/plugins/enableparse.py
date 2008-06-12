#!/usr/bin/python
#
# enableparse.py - parse the enable foo key words to something we can grok
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

import logging

from webKickstart.plugins import TemplateVar
from webKickstart.plugins import WebKickstartPlugin
from webKickstart.errors  import ParseError

log = logging.getLogger('webks')

class EnableParsePlugin(WebKickstartPlugin):

    """
       We have many keywords of the form 'enable <key>' which is parsed as
       'enable' being the keyword.  We need to grok the additional part
       of the keyword.

       This takes the 'enable' keyword if it exists, removes it from the
       variableDict, and inserts 'enable.<key>' for each enable record.
    """

    def run(self):
        """This must return a new dict of variables to use in parsing
           the template."""

        if not self.variableDict.has_key('enable'):
            return self.variableDict

        oldenables = self.variableDict['enable']
        del self.variableDict['enable']
        enable = TemplateVar('', key='enable')

        for record in oldenables:
            if record.len() >= 1:
                if record.len() >= 2:
                    value = record.options()[1:]
                else:
                    value = []
                enable.setMember(record.options()[0], value, noKey=True)
            else:
                raise ParseError, "Found 'enable' keyword with no arguments."

        # A helper method to add variables to the variableDict
        self.addVar(enable)

        return self.variableDict

