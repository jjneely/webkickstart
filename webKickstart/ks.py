# ks.py -- apache mod_python handler
#
# Copyright, 2002 - 2012 Jack Neely <jjneely@ncsu.edu>
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys
import os
import logging

from mod_python import apache

from webKickstart import webKickstart
from webKickstart import configtools

def doSetup(req):
    if req.get_options().has_key('webKickstart.config'):
        configDir = req.get_options()['webKickstart.config']
    else:
        configDir = None

    configtools.config = configtools.Configuration(configDir)


def handler(req):
    # PythonOptions and configuration
    if configtools.config == None:
        doSetup(req)

    # Figure out the user agent
    if req.headers_in.has_key('User-Agent'):
        userAgent = req.headers_in['User-Agent']
    else:
        userAgent = "None"

    # build requested URL
    url = "http://" + req.hostname + req.unparsed_uri

    # Log this request
    log = logging.getLogger("webks")
    log.info("%s - %s - %s - %s" % \
             (req.get_remote_host(apache.REMOTE_NOLOOKUP), url,
              userAgent, req.the_request))
    
    # Main apache request handler
    req.content_type = "text/plain"
    req.send_http_header()

    # Get the IP of the client
    ip = req.get_remote_host(apache.REMOTE_NOLOOKUP)

    # Init webKickstart
    w = webKickstart(url, req.headers_in)

    # Main mode of operation
    # Other cool stuff moved to webapp.py
    tuple = w.getKS(ip)

    # send on the kickstart
    req.write(tuple[1])

    # if error code == 42 we need to log the output because its a traceback
    if tuple[0] == 42: apache.log_error(tuple[1], apache.APLOG_ERR)

    return apache.OK

