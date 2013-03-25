#!/usr/bin/python
#
# webKickstart.py -- finds solaris config file or ks and builds string
#                    to send out apache
#
# Copyright 2002-2012 NC State University
# Written by Jack Neely <jjneely@pams.ncsu.edu> and
#            Elliot Peele <elliot@bentlogic.net>
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

import configtools
from flask import Flask

app = Flask(__name__)

def __init():
    # XXX: How do we read configuration from the WSGI env?
    #if req.get_options().has_key('webKickstart.config'):
    #    configDir = req.get_options()['webKickstart.config']
    #else:
    #    configDir = None

    configDir = None
    configtools.config = configtools.Configuration(configDir)

    # Logging: we currently use our own logging setup
    # and if we tell Flask to use it, Flask wipes out its handlers
    # as it re-creates its logger.  So we add our existing Handlers to
    # the Flask logger
    if not app.debug:
        log = logging.getLogger("webks")
        for h in log.handlers:
            app.logger.addHandler(h)

app.before_first_request(__init)

# Where our response method lives
import webKickstart.ks

