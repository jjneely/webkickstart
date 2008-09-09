# This works in the cherrypy environment to deal with NCSU WRAP
# web authentication

import cherrypy
import pwd
import os

class Auth(object):
    
    def __init__(self):
        try:
            env = cherrypy.request.wsgi_environ
        except AttributeError:
            self.null()

        try:
            self.userid = env['WRAP_USERID']
            self.affiliation = env['WRAP_AFFIL']
            self.expire = env['WRAP_EXPDATE']
            self.ipaddress = env['WRAP_ADDRESS']
        except KeyError:
            self.null()

    def null(self):
        self.userid = None
        self.affiliation = None
        self.expire = None
        self.ipaddress = None

    def isAuthenticated(self):
        return self.userid != None

    def isAuthorized(self):
        cmd = "/usr/bin/pts mem installer:common -c bp"

        if not self.isAuthenticated(): return False

        fd = os.popen(cmd, 'r')
        blob = fd.readlines()
        fd.close()

        for line in blob[1:]:    # throw away first line
            if line.strip() == self.userid:
                return True

        return False

    def getName(self):
        # Note that the users that authenticate will also be in the system's
        # password db (hesiod/ldap)
        if not self.isAuthenticated():
            return "Guest User"
        return pwd.getpwnam(self.userid)[4]        

