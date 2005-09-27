# ks.py -- apache mod_python handler
#
# Copyright, 2002, 2005 Jack Neely <slack@quackmaster.net>
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

from mod_python import apache
from mod_python import util

from webKickstart import webKickstart

import sys,os

def handler(req):
    # Main apache request handler
    req.content_type = "text/plain"
    req.send_http_header()

    # build requested URL
    url = "http://" + req.hostname + req.uri
    
    # set current working dir to something sane
    os.chdir(sys.path[0])

    # Get the IP of the requestor
    ip = req.get_remote_host(apache.REMOTE_NOLOOKUP)

    # Init webKickstart
    w = webKickstart(url, req.headers_in)

    # get the GET/POST thingies
    args = util.FieldStorage(req)
    
    # Check to see what mode to run in
    if 'collision_detection' in args.keys():
        tuple = w.collisionDetection(args['collision_detection'])
        
    elif 'dns_config_check' in args.keys():
        tuple = w.checkConfigHostnames()
        
    elif 'debugtool' in args.keys():
        # Pass what we intered into the debug field and turn on debug mode
        tuple = w.getKS(args['debugtool'], 1)
        
    else:
        # Main mode of operation
        tuple = w.getKS(ip, 0)

    # send on the kickstart
    req.write(tuple[1])

    # if error code == 42 we need to log the output because its a traceback
    if tuple[0] == 42: apache.log_error(tuple[1], apache.APLOG_ERR)

    return apache.OK

