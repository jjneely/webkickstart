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
for i in ks.table:
   print i

print ks.language()
print ks.install()
print ks.partition()
print ks.inputdevs()
print ks.xconfig()
print ks.rootwords()
print ks.packages()
print ks.startPost()
print ks.reinstall()
print ks.admins()
print ks.sendmail()

#print ks.pullUsers('pams')
#print ks.pullRoot('pams')
