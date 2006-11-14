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
import MySQLdb
import time
import os
import os.path 

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


def getDB():
    # Return information about DB
    # returns (host, user, passwd, db)
    host = cfg.db['host']
    user = cfg.db['user']
    passwd = cfg.db['passwd']
    db = cfg.db['db']

    return (host, user, passwd, db)


def loghost(fqdn):
    # Log this install in the DB
    ts = time.localtime()
    date = MySQLdb.Timestamp(ts[0], ts[1], ts[2], ts[3], ts[4], ts[5])

    host, user, passwd, db = getDB()
    conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    cursor = conn.cursor()

    cursor.execute("select hostname from realmlinux where hostname=%s", 
                   (fqdn,))
    if cursor.rowcount > 0:
        # If the client exists in DB assume its getting reinstalled
        q = """update realmlinux set 
               installdate = %s, 
               recvdkey = 0,
               publickey = NULL,
               dept = '',
               version = '',
               support = 1
               where hostname = %s"""
        t = (date, fqdn)
    else:
        q = """insert into realmlinux 
               (hostname, installdate, recvdkey, publickey, dept, version,
                support) values
               (%s, %s, 0, NULL, '', '', 1)"""
        t = (fqdn, date)

    # Set the host, date, and received_key status.
    # Other values get set at host registration
    cursor.execute(q, t)
    
    cursor.close()
    conn.commit()
    conn.close()


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
    
