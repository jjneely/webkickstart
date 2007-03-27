#!/usr/bin/python
#
# exceptions.py -- handles some custom exceptions
#
# Copyright, 2002 Jack Neely <slack@quackmaster.net>
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

class WebKickstartError(StandardError): pass

class ParseError(WebKickstartError):
    
    def __init__(self, value="A parsing error has occured."):
        self.value = value
        
    def __str__(self):
        return self.value
        

class AccessError(WebKickstartError):

    def __init__(self, value="An access error has occured."):
        self.value = value

    def __str__(self):
        return self.value


class ConfigError(WebKickstartError):
                                                                                
    def __init__(self, value="A config error has occured."):
        self.value = value
                                                                                
    def __str__(self):
        return self.value

