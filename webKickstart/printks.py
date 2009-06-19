#!/usr/bin/python
#
# printks.py -- Debugging Tool for Web-Kickstart
#
# Copyright, 2002, 2005 NC State University
# Written by Jack Neely <jjneely@pams.ncsu.edu>
#
# SDG
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# This is a debugging tool for Web-Kickstart.  Execute this script at the
# top level of the CVS checkout, tarball, install, and provide a host
# name as its only argument and this script will print out the kickstart
# that host would receive.  Does not go through apache.

from webKickstart import webKickstart
import sys,os,socket
import config

# Setup configfile
cfg = config.webksconf('./solaris2ks.conf')
webKickstart.cfg = cfg

# Get host name
host = sys.argv[1]

# Get ip address
ip = socket.gethostbyname(host)

# build requested URL
url = "http://web-kickstart.linux.ncsu.edu/ks.py"

# Init webKickstart
w = webKickstart(url, {})
tuple = w.getKS(ip, debug=1)
print tuple[1]


