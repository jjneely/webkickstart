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
ks.includeFile(solarisConfig('examples/pams-server'))
for i in ks.table:
   print i

