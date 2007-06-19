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
    if len(sys.argv) == 2:
        # Try to pull from web-kickstart
        uri = "%s?debugtool=%s" % (url, sys.argv[1])
        ksfd = urllib2.urlopen(uri)
        data = ksfd.read()

        fileno, filename = tempfile.mkstemp()
        fd = open(filename, 'w')
        fd.write(data)
        fd.close()
    else:
        # or --filename foo
        # I just don't care how bad I do arguments here
        filename = sys.argv[2]
        data = open(filename).read()

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
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print "Usage: %s <hostname>" % sys.argv[0]
        print "Usage: %s --filename <kickstart.cfg>" % sys.argv[0]
    else:
        main()

