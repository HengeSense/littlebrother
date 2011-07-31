#-*- coding: UTF-8

import re

splitter = re.compile(
	ur'([,\.!\?:;\s\n\t])'
	, re.UNICODE)


def tokenize(string):
	'''Split string to words'''
	return [ 
		item.strip() for item in splitter.split(string) if len(item.strip()) > 0 
	]

if __name__ == '__main__':
	import unittest
	
	class TokenizerTest(unittest.TestCase):
		
		def testIt(self):
			tokens = [ u'хуй', u'пизда', u'анархия' ]
			dirty_tokens = [ token + u'!' for token in tokens ]
			
			assert(tokenize(' '.join(tokens)) == tokens)
			assert(len(tokenize(' '.join(dirty_tokens))) == len(tokens) * 2)
	
	unittest.main()
