#!/usr/bin/python
#
# testconfig.py
# Copyright (C) 2007 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
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
import sys
import os.path
import unittest

sys.path.insert(0, "../")

from webKickstart import config
from webKickstart.solarisConfig import solarisConfig as MetaParser

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.cfg = config.Configuration('testconfig/')
    
    def test1(self):
        pass


if __name__ == '__main__':
    unittest.main()

