#!/usr/bin/python
#
# setup.py - Distutils setup
#
# Copyright 2008 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
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

import os
import os.path
from distutils.core import setup
from glob import glob

VERSION="3.0"

def getDirs(path):
    # Split up a directory listing of files and directories into
    # the python packages to suck in
    dirs = [path.replace('/', '.')]

    dir = os.listdir(path)
    for node in dir:
        apath = os.path.join(path, node)
        if ".svn" in apath: 
            continue
        if ".git" in apath:
            continue
        if os.path.isdir(apath):
            dirs.extend(getDirs(apath))

    return dirs

setup(  version=VERSION,

        name="Web-Kickstart",
        description="Dynamically build complex Kickstarts.",
        author="Jack Neely",
        author_email="linux@help.ncsu.edu",
        url="https://secure.linux.ncsu.edu/moin/WebKickstart",

        packages=getDirs('webKickstart'),
        package_data={'webKickstart': ['webtmpl/*.kid',
                                       'static/*.png',
                                       'static/*.gif',
                                       'static/css/*.css'],
                     },
        data_files=[('/etc/webkickstart', ['etc/webkickstart.conf']),
         ('/etc/webkickstart/hosts', glob('etc/hosts/*')),
         ('/etc/webkickstart/pluginconf.d', glob('etc/pluginconf.d/*.example')),
         ('/etc/webkickstart/profiles', glob('etc/profiles/*.tmpl')),
        ],
        scripts=['scripts/makekickstart.py',
                 'scripts/simplewebkickstart.py'],
     )
