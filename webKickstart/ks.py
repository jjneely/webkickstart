# ks.py -- apache mod_python handler
#
# Copyright, 2002 - 2008 Jack Neely <jjneely@ncsu.edu>
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

from mod_python import apache

from webKickstart import webKickstart

def handler(req):
    # Main apache request handler
    req.content_type = "text/plain"
    req.send_http_header()

    # build requested URL
    url = "http://" + req.hostname + req.uri
    
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

