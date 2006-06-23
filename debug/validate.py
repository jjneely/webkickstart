#!/usr/bin/python

# Validate a kickstart

import sys
import urllib2
import tempfile

try:
    from pykickstart.data import *
    from pykickstart.parser import *
except ImportError:
    print "You need the pykickstart package installed to run this test."
    sys.exit(1)

url = "http://web-kickstart.linux.ncsu.edu/ks.py"

def main():
    uri = "%s?debugtool=%s" % (url, sys.argv[1])
    ksfd = urllib2.urlopen(uri)
    data = ksfd.read()

    fileno, filename = tempfile.mkstemp()
    fd = open(filename, 'w')
    fd.write(data)
    fd.close()

    ksdata = KickstartData()
    kshandler = KickstartHandlers(ksdata)
    parser = KickstartParser(ksdata,
                             kshandler,
                             followIncludes=False,
                             errorsAreFatal=True)

    try:
        parser.readKickstart(filename)
    except KickstartParseError, e:
        print "The kickstart is not valid"
        print "Error message: %s" % str(e)

        try:
            line = int(str(e).split()[6])
        except ValueError:
            line = None

        if line is not None:
            print "Line %s: %s" % (line, data.split('\n')[line-1])


if __name__ == "__main__":
    if len(sys.argv) is not 2:
        print "Usage: %s <hostname>" % sys.argv[0]
    else:
        main()

