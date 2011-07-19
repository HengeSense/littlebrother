#-*- coding: UTF-8

import simplejson


def dump(data):
	"""Dumps list to JSON format"""
	
	yield '['
	for index, chunk in enumerate(data):
		if index > 0:
			yield ','
		
		yield simplejson.dumps(chunk, separators = (',', ':'))
	yield ']'


if __name__ == '__main__':
	import unittest

	unittest.main()
