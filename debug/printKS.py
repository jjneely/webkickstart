#!/usr/bin/python

import os
import sys
#sys.path.append('../')
#sys.path.append('./')
import socket
from webKickstart import webKickstart
from webKickstart import config, solarisConfig

os.chdir('../')

try:
    ip = socket.gethostbyname(sys.argv[1])
    wk = webKickstart('http://foo.bar',None)
    ks = wk.getKS(ip, debug=1)
    print ks[1]
except:
    #import config
    #from solarisConfig import solarisConfig
    cfg = config.webksconf()
    sc = solarisConfig(sys.argv[1])
    gen = cfg.get_obj(sc.getVersion(), {'url': 'http://foo.bar', 'sc': sc})
    print gen.makeKS()

