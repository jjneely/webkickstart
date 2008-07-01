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

import cherrypy
import sys
import os
import kid 

from webKickstart import webKickstart
from webKickstart import configtools

def importer(module):
    tree = module.split('.')
    for path in sys.path:
        basepath = apply(os.path.join, [path] + tree[:-1])
        file = os.path.join(basepath, tree[-1]+'.kid')
        if os.path.exists(file):
            return kid.Template(file=file)

    return None

def serialize(mod, dict):
    #template = importer(mod)
    template = kid.Template(name=mod)
    if template == None:
        raise Exception("No kid module %s" % mod)

    for key, value in dict.items():
        setattr(template, key, value)

    return template.serialize(encoding='utf-8', output='xhtml')

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

class Application(object):

    def index(self):
        pass


def main():
    cherrypy.root = Application()
    cherrypy.server.start()

if __name__ == "__main__":
    main()
