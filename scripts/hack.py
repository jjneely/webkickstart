#!/usr/bin/python

import urllib2
import sys

if len(sys.argv) != 2:
    print "Usage: %s <URl>" % sys.argv[0]
    sys.exit(1)
    
url = sys.argv[1]

req = urllib2.Request(url, headers={})

# Reach down into the depths of urllib and muck with stuff
# X-RHN-Provisioning-MAC-0
director = urllib2.build_opener()
director.addheaders = [('X-RHN-Provisioning-MAC-0','foo')]
urllib2.install_opener(director)

try:
    fd = urllib2.urlopen(req)
    print fd.read()
    fd.close()
except urllib2.HTTPError, e:
    print str(e)


