#!/usr/bin/python

# Validate a kickstart

import sys
import urllib2
import tempfile
import pykickstart

url = "http://web-kickstart.linux.ncsu.edu/ks.py"

def main():
    uri = "%s?debugtool=%s" % (url, sys.argv[1])
    ksfd = urllib2.urlopen(uri)
    data = ksfd.read()
    print data

    fileno, filename = tempfile.mkstemp()
    fd = open(filename, 'w')
    fd.write(data)
    fd.close()

    ksdata = pykickstart.data.KickstartData()
    parser = pykickstart.parser.KickstartParser(ksdata,
                                         None,
                                         followIncludes=False,
                                         errorsAreFatal=True)
    
    parser.readKickstart(filename)

if __name__ == "__main__":
    main()
