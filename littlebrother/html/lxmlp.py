#-*- coding: UTF-8

from lxml import etree
import chardet.universaldetector
import re

charset_regex = re.compile(
	ur'''content\s?=\s?[^>]*charset\s?=\s?([^/>"\s]+)''', 
	re.UNICODE | re.IGNORECASE | re.VERBOSE)


def extract_charset(filep):
	'''Extract charset (if any) from HTML document'''
	
	for line in filep.readlines():
		groups = charset_regex.search(line)
		if groups:
			return groups.group(1)


def parse_file(filep, providers):
	'''
	Search identities in (supposedly HTML) file, returns (identity, xpath, tag) list
	
	Argument providers is a list of (provider, tag), where provider is callable
	'''

	def walk_node(doc, node):
		if node == None:
			return []
		
		ret = []
		if node.text or node.tail:
			for provider, tag in providers:
				identities = provider(node.text or node.tail)
				xpath = doc.getpath(node.text and node or node.getparent())
				
				for identity in identities:
					ret.append((identity, xpath, tag))
		
		for child in node:
			ret += walk_node(doc, child)
		
		return ret
	
	if not providers:
		return []
	
	filep.seek(0)

	charset = extract_charset(filep)

	if not charset: 
		filep.seek(0)
		charset = guess_encoding(filep)

	filep.seek(0)

	parser = etree.HTMLParser(encoding = charset)
	doc = etree.parse(filep, parser)
	
	title = doc.xpath('//title/text()')
	title = (title and title[0] or None)
	
	if title == None:
		title = doc.xpath('//h1/text()')
		title = (title and title[0] or None)
	
	if title == None:
		title = doc.xpath('//h2/text()')
		title = (title and title[0] or None)
	
	return (title and unicode(title) or None, walk_node(doc, doc.getroot()))


def guess_encoding(filep):
	'''Guess encoding of a file'''

	detector = chardet.universaldetector.UniversalDetector()
	try:
		for line in filep.readlines():
			detector.feed(line)
			if detector.done:
				break
	finally:
		detector.close()

	encoding = detector.result.get('encoding', 'UTF-8')
	return encoding


if __name__ == '__main__':
	import unittest
	import ident.names
	import StringIO

	class ChardetTest(unittest.TestCase):
		files = [ 
			('samples/test.html', 'utf-8')
		]
	
		def testGuess(self):
			for filename, encoding in self.files:
				assert(guess_encoding(open(filename, 'r')).lower() == encoding.lower())

	class ParseTest(unittest.TestCase):
		filename = 'samples/test.html'
	
		def testIt(self):
			title, identities = parse_file(
				open(self.filename, 'r'), 
				((ident.names.identities, 'test'), ))
			
			assert(title)
#			for identity, xpath in identities:
#				print identity, xpath
			assert(len(identities) > 0)
			
			identity, xpath, tag = identities[0]
			
			assert(identity)
			assert(xpath)
			assert(tag and tag == 'test')
		
		def testCharsetExtract(self):
			assert(extract_charset(StringIO.StringIO('<meta http-equiv="content-type" content="text/html; charset=windows-1251">')) == 'windows-1251')
			assert(extract_charset(StringIO.StringIO('''<meta
				http-equiv="content-type"
				content="text/html; charset=windows-1251">''')) == 'windows-1251')
		
		def testTail(self):
			testcase = "<p>был Петров Иван<br />стал Иванов Пётр</p>"
			title, identities = parse_file(
				StringIO.StringIO(testcase), 
				((ident.names.identities, 'test'), ))
			
			assert(len(identities) == 2)
	
	unittest.main()
