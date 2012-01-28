#-*- coding: UTF-8

import re

sql_valid_chars = ur"""0-9a-zа-яё /.,'":\-()<>!&@"""

sql_validator = re.compile(
	ur"""^[""" + sql_valid_chars + """]+$"""
	, re.UNICODE | re.IGNORECASE | re.VERBOSE)

sql_escaper = re.compile(
	ur"""[^""" + sql_valid_chars + """]"""
	, re.UNICODE | re.IGNORECASE | re.VERBOSE)


def sql_valid(string):
	"""Check if string is SQL-valid"""
	return (sql_validator.match(string) != None)


def sql_escape(string):
	"""Escape SQL-string"""
	return (sql_escaper.sub(u'.', string))


if __name__ == '__main__':
	import unittest

	class SQLValidatorTest(unittest.TestCase):

		def testIt(self):
			assert(sql_valid(u'10 Little nigger boys went out to dine'))
			assert(sql_valid(u'10 Негритят решили пообедать'))

			valid_chars = u"""-.,ёЁйЙAZaz"'/()<>&!@"""
			for char in valid_chars:
				if not sql_valid(char):
					self.fail('"' + char.encode('UTF-8') + '" appears to be invalid SQL character')

			invalid_chars = u"""~`#$%^*_=+[{]}\|;?"""
			for char in invalid_chars:
				if sql_valid(char):
					self.fail('"' + char.encode('UTF-8') + '" appears to be valid SQL character')

	class SQLEscaperTest(unittest.TestCase):

		def testIt(self):
			testcases = [
				(u'роисся вперде', u'роисся вперде'),
				(u"'; DROP DATABASE skotobaza --", u"'. DROP DATABASE skotobaza --"),
			]

			for (input, output) in testcases:
				assert(sql_escape(input) == output)

	unittest.main()
