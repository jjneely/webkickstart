#!/usr/bin/python

import sys
import socket
from webKickstart import webKickstart

ip = socket.gethostbyname(sys.argv[1])
wk = webKickstart('http://foo.bar',None)
ks = wk.getKS(ip, debug=1)
print ks[1]
