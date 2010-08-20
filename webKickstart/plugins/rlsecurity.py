#!/usr/bin/python
#
# rlsecurity.py -- Security logging
#
# Copyright 2003 - 2008 NC State University
# Written by Jack Neely <jjneely@pams.ncsu.edu>
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
import os.path 
import xmlrpclib
import logging

from webKickstart.plugins import WebKickstartPlugin
from webKickstart.plugins import TemplateVar
from webKickstart.errors  import *

log = logging.getLogger("webks")

class LiquidDragonPlugin(WebKickstartPlugin):

    def run(self):
        if not self.debug:
            # Debug modes are on for the website kickstart preview 
            fqdn = str(self.variableDict["webKickstart"].remoteHost)
            self.loghost(fqdn)
        else:
            log.info("Debug mode detected, not logging install for %s",
                     self.variableDict['webKickstart'].remoteHost)

        return self.variableDict

    def loghost(self, fqdn):
        # Log this install in the DB
        server = self.cfg.get('main', 'server', None)
        secret = self.cfg.get('main', 'secret', None)

        if server == None or secret == None:
            msg = "Missing server or secret values in rlsecurity.conf."
            raise WebKickstartError, msg

        log.debug("Using XMLRPC API: %s" % server)
        api = xmlrpclib.ServerProxy(server)

        try:
            # Use RLMTools APIv2 and remember the session hash
            code, sid = api.initHost(2, secret, fqdn)
        except Exception, e:
            raise WebKickstartError("Error initalizing %s with RLM Tools XMLRPC interface.  Halting.\nError: %s" % (fqdn, str(e)))

        if code == 0:
            return
        elif code == 1:
            raise WebKickstartError("Error initalizing %s with RLM Tools XMLRPC interface.  Halting.\nBad authentication." % fqdn)
        else:
            raise WebKickstartError("Error initalizing %s with RLM Tools XMLRPC interface.  Halting.\nUnknown error code: %s." % (fqdn, code))

        self.addVar(TemplateVar(['rlmtools-session', sid]))

