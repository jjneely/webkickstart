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
import logger

from webKickstart import webKickstart

log = logger.getLogger("webks")

class WebKSHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        log.info("WebKickstart request from %s" % self.client_address)
        log.debug("Headers: %s" % str(self.headers))

        w = webKickstart("url", self.headers)
        tuple = w.getKS(ip, 0)

        self.send_header('content_type', "text/plain")

        if tuple[0] != 0:
            log.warning("Something bad happend.")
            log.warning(tuple[1])

        return tuple[1]


def main():
    pass

