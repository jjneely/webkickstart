#!/usr/bin/python
#
# basicserver.py
#
# Copyright 2008 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
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

import BaseHTTPServer
import optparse
import logging
import sys

from webKickstart import webKickstart
from webKickstart import configtools

log = logging.getLogger("webks")

class WebKSHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        #log.info("WebKickstart request from %s" % self.client_address)
        log.debug("Headers: %s" % str(self.headers))

        w = webKickstart("url", self.headers)
        tuple = w.getKS(self.address_string())

        if tuple[0] != 0:
            log.warning("Returning error message to client.")

        self.send_response(200)
        self.send_header('Content_type', 'text/plain')
        self.end_headers()

        self.wfile.write(tuple[1])

    def log_message(self, format, *args):
        log.info("%s - - %s" % (self.address_string(),
                                format % args))


def main():
    parser = optparse.OptionParser("%%prog %s [options]" % \
                                   sys.argv[0])
    parser.add_option("-C", "--configdir", action="store", type="string",
           dest="configdir", default=None,
           help="Configuration directory. [/etc/webkickstart]")
    parser.add_option("-p", "--port", action="store", type="int",
           dest="port", default=8080,
           help="HTTP Port. [8080]")

    (opts, args) = parser.parse_args(sys.argv)
    
    if len(args) > 1:
        parser.print_help()
        sys.exit(1)

    cfg = configtools.Configuration(opts.configdir)
    configtools.config = cfg

    log.info("Hit ^C to terminate.")

    httpd = BaseHTTPServer.HTTPServer(('', opts.port), WebKSHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    log.info("Shutting down...")

if __name__ == "__main__":
    main()

