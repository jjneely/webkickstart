#!/usr/bin/python
#
# shreak.py -- class to generate kickstart from solars config for rk9
#
# Elliot Peele <elliot@bentlogic.net>
# Copyright 2003 NC State University
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

"""This module contains the class used to generate a FC1 kickstart."""

import string
import shreak

class yarrow(shreak.shreak):
    version = "FC1"

