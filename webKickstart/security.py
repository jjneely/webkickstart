#!/usr/bin/python
#
# security.py -- Security checks for webKickstart
#
# Copyright 2003, 2006 NC State University
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

import config
import errors
import os
import os.path 
import xmlrpclib
import logging

log = logging.getLogger("webks")

def check(headers, fqdn):
    # check for anaconda
    if headers.has_key("X-RHN-Provisioning-MAC-0"):
        # continue through...we *know* this is anaconda
        # only present in version >= FC1
        pass
    elif len(headers) > 1:
        # Bad
        return 0
    elif not headers.has_key('Host'):
        # More bad
        return 0

    # Okay I'm pretty sure this must be anaconda now...although it
    # would be nice to have a better indication

    loghost(fqdn)

    return 1


def loghost(fqdn):
    # Log this install in the DB
    log.debug("Using XMLRPC API: %s" % config.config.xmlrpc)
    api = xmlrpclib.ServerProxy(config.config.xmlrpc)
    apiSecret = config.config.secret

    try:
        code = api.initHost(apiSecret, fqdn)
    except Exception, e:
        raise errors.WebKickstartError("Error initalizing %s with RLM Tools XMLRPC interface.  Halting.\nError: %s" % (fqdn, str(e)))

    if code == 0:
        return
    elif code == 1:
        raise errors.WebKickstartError("Error initalizing %s with RLM Tools XMLRPC interface.  Halting.\nBad authentication.")
    else:
        raise errors.WebKickstartError("Error initalizing %s with RLM Tools XMLRPC interface.  Halting.\nUnknown error code: %s." % code)


def rootMD5(group, key=None):
    """Returns the MD5 Hash for the root password for this admin group
       or, on failure the default MD5 hash."""

    return _decryptData('root.md5', group, key)


def adminUsers(group, key=None):
    """Returns a list of admin users.  If the list for the admin group is 
       not found the default list will be returned."""

    data = _decryptData('users', group, key)

    list = data.split()
    return list


def _decryptData(what, group, key=None):
    """Returns a stripped string of data.  what can be 'root.md5' or 'users'.
       Pulls information out of the conftree."""

    defaultkey = cfg.defaultkey
    conftree = '/afs/bp.ncsu.edu/system/common/update'
    openssl = '/usr/bin/openssl'
    
    if key == None:
        #print "key is None...using default"
        group = 'default'
        key = defaultkey
    else:
        # check if group exists
        path = os.path.join(conftree, what, group)
        if not os.access(path, os.R_OK):
            #print "Data file missing, using default"
            group = 'default'
            key = defaultkey
    
    path = os.path.join(conftree, what, group)
    command = "%s bf -d -k %s -in %s" % (openssl, key, path)
    pipe = os.popen(command)
    stuff = pipe.read().strip()
    ret = pipe.close()
    if not ret == None:
        raise StandardError,"Blowfish decryption failed in security.decryptData"

    return stuff
    
