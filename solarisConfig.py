#!/usr/bin/python
#
# solarisConfig.py -- tools for parsing solaris config files
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

import string
import shlex
import cStringIO

class solarisConfig:
	"""This class has tools and functions for parsing a solaris config file.
	   We can recognize if this is a normal kickstart instead.  This class is
	   ment to be used by a factory class to produce a Red Hat Kickstart."""
	   
	filedata = ""
	filecommands = []
	fileposts = []
	
	def __init__(self, filename):
		file = open(filename)
		# Do we need to handle exception or let them propigate up?
		
		self.filedata = file.read()
		file.close()
		lines = string.split(self.filedata, '\n')
		self.filecommands, self.fileposts = self.__splitFile(lines)
		
		
	def __splitFile(self, lines):
		"""Separates the file into the first part of commands and the second
		   part containing any %post, %pre, %packages, %anything."""
		
		breakpoint = 0
		for line in lines:
			s = string.strip(line)
			print s
			if len(s) > 0 and s[0] == "%":
				break
			breakpoint = breakpoint + 1
			
		return lines[0:breakpoint], lines[breakpoint:]
		
		
	def isKickstart(self):
		"""Return true if this config file appears to be a kickstart"""
		
		ksReqs = ['auth', 'keyboard', 'lang', 'mouse', 'rootpw', 'timezone']
		coms = self.getListOfKeys()
		ret = 1
		
		for key in ksReqs:
			if ret == 1 and key not in coms:
				# this is not a ks
				ret = 0

		return ret
		
		
	def getLine(self, num):
		"""Returns a dict containing 'key' and 'options' found on this line number.
		   This assumes you are looking in the commands section."""
		
		if num >= len(self.filecommands):
			return None
		
		s = cStringIO.StringIO(self.filecommands[num])
		dict = {}
		lex = shlex.shlex(s)
		dict['key'] = lex.get_token()
		ops = []
		s2 = lex.get_token()
		while not s2 == "":
			ops.append(s2)
			s2 = lex.get_token()
		dict['options'] = ops
		
		return dict
		
		
	def getCommands(self):
		"""Returns a string of the commands section of the file."""
		
		return string.join(self.filecommands, '\n')
		
		
	def getPost(self):
		"""Returns a string of the rest of the file including the first % command."""
		
		return string.join(self.fileposts, '\n')
		
		
	def getFile(self):
		"""Return a string of the entire config file."""
		
		return self.filedata
		
		
	def getListOfKeys(self):
		"""Return a list of all keywords used in config file."""

		coms = []
		for i in range(len(self.filecommands)):
			dict = self.getLine(i)
			if dict != None and dict['key'] != '':
				coms.append(dict['key'])	
			
		return coms
		
		
	
