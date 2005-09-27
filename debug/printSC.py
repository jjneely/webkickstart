#!/usr/bin/python
#
# test2.py - prints out the dict of options after reading a user defined file
#
# Elliot Peele <elliot@bentlogic.net>
# Copyright 2003
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import sys
sys.path.append('../')
from solarisConfig import solarisConfig
import pprint

cf = solarisConfig(sys.argv[1])
pp = pprint.PrettyPrinter(indent=4)

tmp = cf.parseCommands()

pp.pprint(tmp)
