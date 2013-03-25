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

from flask import request, abort, Response

from webks import webKickstart

# The Flask app
from webKickstart import app

@app.route("/ks.py", methods=["GET"])
def handler():
    # Figure out the user agent
    if request.headers.has_key('User-Agent'):
        userAgent = request.headers['User-Agent']
    else:
        userAgent = "None"

    # build requested URL
    url = request.url

    # Log this request
    log = logging.getLogger("webks")
    log.info("%s - %s - %s - %s" % \
             (request.remote_addr, url, userAgent, request.method))
    
    # Get the IP of the client
    ip = request.remote_addr

    # Init webKickstart
    w = webKickstart(url, request.headers)

    # Main mode of operation
    tuple = w.getKS(ip)

    # if error code == 42 we need to log the output because its a traceback
    if tuple[0] == 42: 
        code = "500 Internal server error"
    else:
        code = "200 OK"

    return Response(tuple[1], status=code, mimetype="text/plain")

