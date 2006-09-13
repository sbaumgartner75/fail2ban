# This file is part of Fail2Ban.
#
# Fail2Ban is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Fail2Ban is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fail2Ban; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Author: Cyril Jaquier
# 
# $Revision$

__author__ = "Cyril Jaquier"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2004 Cyril Jaquier"
__license__ = "GPL"

import unittest, socket
from server.filter import Filter
from server.failmanager import FailManager

class IgnoreIP(unittest.TestCase):

	def setUp(self):
		"""Call before every test case."""
		self.filter = Filter(None)

	def tearDown(self):
		"""Call after every test case."""

	def testIgnoreIPOK(self):
		ipList = "127.0.0.1", "192.168.0.1", "255.255.255.255", "99.99.99.99"
		for ip in ipList:
			self.filter.addIgnoreIP(ip)
			self.assertTrue(self.filter.inIgnoreIPList(ip))
	
	def testIgnoreIPNOK(self):
		ipList = "", "999.999.999.999", "abcdef", "192.168.0"
		for ip in ipList:
			self.filter.addIgnoreIP(ip)
			self.assertFalse(self.filter.inIgnoreIPList(ip))


class LogFile(unittest.TestCase):

	filename = "testcases/files/testcase01.log"

	def setUp(self):
		"""Call before every test case."""
		self.filter = Filter(None)
		self.filter.addLogPath(LogFile.filename)

	def tearDown(self):
		"""Call after every test case."""
		
	def testOpen(self):
		self.filter.openLogFile(LogFile.filename)
	
	def testIsModified(self):
		self.assertTrue(self.filter.isModified(LogFile.filename))


class GetFailures(unittest.TestCase):

	def setUp(self):
		"""Call before every test case."""
		self.filter = Filter(None)
		self.filter.addLogPath("testcases/files/testcase01.log")
		self.filter.setTimeRegex("\S{3}\s{1,2}\d{1,2} \d{2}:\d{2}:\d{2}")
		self.filter.setTimePattern("%b %d %H:%M:%S")
		self.filter.setFailRegex("(?:(?:Authentication failure|Failed [-/\w+]+) for(?: [iI](?:llegal|nvalid) user)?|[Ii](?:llegal|nvalid) user|ROOT LOGIN REFUSED) .*(?: from|FROM) (?:::f{4,6}:)?(?P<host>\S*)")

	def tearDown(self):
		"""Call after every test case."""
		
	def testGetFailures(self):
		output = [('87.142.124.10', 3, 1167605999.0),
				  ('193.168.0.128', 3, 1167605999.0)]

		self.filter.openLogFile()
		self.filter.getFailures()
		
		found = []
		for ip in self.filter.failManager.failList:
			fData = self.filter.failManager.failList[ip]
			retry = fData.getRetry()
			lTime = fData.getLastTime()
			found.append((ip, retry, lTime))
		self.assertEqual(found, output)
		