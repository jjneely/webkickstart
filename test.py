#!/usr/bin/python

from solarisConfig import *

cf = solarisConfig('examples/linux-box')
#p = cf.parseCommands()
#for i in p:
#    print i
#	
#print cf.getVersion()
#print cf.isKickstart()
#
#cf = solarisConfig('examples/ks.cfg')
#print cf.isKickstart()

from baseKickstart import *

ks = baseKickstart(cf)
#ks.includeFile(solarisConfig('examples/pams-server'))
#for i in ks.table:
#   print i

## print ks.language()
## print ks.install()
## print ks.partition()
## print ks.inputdevs()
## print ks.xconfig()
## print ks.rootwords()
## print ks.packages()
## print ks.startPost()
## print ks.reinstall()
## print ks.admins()
## print ks.sendmail()
## print ks.consolelogin()
## print ks.notempclean()
## print ks.clusters()
## print ks.department()
## print ks.printer()
## print ks.realmhooks()

#print ks.makeKS()

#print ks.pullUsers('pams')
#print ks.pullRoot('pams')

import socket
import webKickstart
#print socket.gethostbyaddr("anduril.pams.ncsu.edu")

go = webKickstart.webKickstart("http://MY SERVER HERE/")
t = go.getKS('anduril.pams.ncsu.edu')
print t[1]
