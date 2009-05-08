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

import optparse
import cherrypy
import sys
import os
import os.path

from genshi.template import TemplateLoader

from webKickstart import webKickstart
from webKickstart import configtools

# How to better handle web authentication?
from webKickstart.plugins import webauth

class Application(object):

    def __init__(self):
        self.loader = TemplateLoader([os.path.join(os.path.dirname(__file__), 
                                                   'webtmpl')])

        # Create a webKickstart instance to pre-cache the configs
        w = webKickstart('url', {})
        w.buildCache()

    def render(self, tmpl, dict):
        compiled = self.loader.load('%s.xml' % tmpl)
        stream = compiled.generate(**dict)
        return stream.render('xhtml')

    def index(self):
        auth = webauth.Auth()
        name = auth.getName()

        if not auth.isAuthorized():
            return self.render('notauth', dict(name=name))
        
        return self.render('index', dict(name=name))
    index.exposed = True

    def rawKickstart(self, host):
        auth = webauth.Auth()
        if not auth.isAuthorized():
            return self.render('notauth', dict(name=auth.getName()))

        host = host.strip()
        w = webKickstart('url', {})
        w.setDebug(True)           # Previent running of things that shouldn't
                                   # for preview mode
        tuple = w.getKS(host)

        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return tuple[1]
    rawKickstart.exposed = True

    def debugtool(self, host):
        auth = webauth.Auth()
        if not auth.isAuthorized():
            return self.render('notauth', dict(name=auth.getName()))
        
        host = host.strip()
        if host == "":
            return self.render('debugtool', dict(host="None",
                  kickstart="# You failed to provide a host to check."))

        w = webKickstart('url', {})
        w.setDebug(True)           # Previent running of things that shouldn't
                                   # for preview mode
        tuple = w.getKS(host)

        return self.render('debugtool', dict(host=host, kickstart=tuple[1]))
    debugtool.exposed = True

    def collision(self, host):
        auth = webauth.Auth()
        if not auth.isAuthorized():
            return self.render('notauth', dict(name=auth.getName()))
        
        host = host.strip()
        if host == "":
            return self.render('debugtool', dict(host="None",
                  kickstart="# You failed to provide a host to check."))
        
        w = webKickstart('url', {})
        tuple = w.collisionDetection(host)
        return self.render('collision', dict(host=host, output=tuple[1]))
    collision.exposed = True

    def checkconfigs(self):
        auth = webauth.Auth()
        if not auth.isAuthorized():
            return self.render('notauth', dict(name=auth.getName()))
        
        w = webKickstart('url', {})
        tuple = w.checkConfigHostnames()

        return self.render('checkconfigs', dict(output=tuple[1]))
    checkconfigs.exposed = True


def main():
    parser = optparse.OptionParser("%%prog %s [options]" % \
                                   sys.argv[0])
    parser.add_option("-C", "--configdir", action="store", type="string",
           dest="configdir", default=None,
           help="Configuration directory. [/etc/webkickstart]")
    
    (opts, args) = parser.parse_args(sys.argv)
    
    if len(args) > 1:
        parser.print_help()
        sys.exit(1)

    cfg = configtools.Configuration(opts.configdir)
    # XXX: We know that security checks wont work for the webapp
    cfg.security = "0"
    configtools.config = cfg

    # XXX: Static directory.  Hopefully relative...
    staticDir = os.path.join(os.path.dirname(__file__), "static")
    cherrypy.config.update({"/static": {
                            'static_filter.on': True,
                            'static_filter.dir': os.path.abspath(staticDir) }})

    cherrypy.root = Application()
    cherrypy.server.start()

def wsgi(req):
    if req.get_options().has_key('webKickstart.config'):
        configDir = req.get_options()['webKickstart.config']
    else:
        configDir = None

    if req.get_options().has_key('webKickstart.appMount'):
        appMount = req.get_options()['webKickstart.appMount']
    else:
        appMount = None

    cfg = configtools.Configuration(configDir)
    # XXX: We know that security checks wont work for the webapp
    cfg.security = "0"
    configtools.config = cfg

    staticDir = os.path.join(os.path.dirname(__file__), "static")
    if appMount is None:
        staticMount = "/static"
    else:
        staticMount = os.path.join('/', appMount, 'static')

    cherrypy.config.update({staticMount: {
                            'static_filter.on': True,
                            'static_filter.dir': os.path.abspath(staticDir) }})

    cherrypy.config.update({"server.environment": "production",
                            "server.protocolVersion": "HTTP/1.1",
                            "server.log_file": "/var/log/webkickstart-cherrypy.log"})

    if appMount is None:
        cherrypy.root = Application()
    else:
        cherrypy.tree.mount(Application(), appMount)

    cherrypy.server.start(initOnly=True, serverClass=None)

if __name__ == "__main__":
    main()

