#-*- coding: UTF-8

import re

ignored_tags = 'a/b/strong/i/em/strike/font/h1/h2/h3/h4/h5/h6'.split('/')
xpath_index = re.compile(u'\[(\d+)\]')


def xpath_distance(xpath_a, xpath_b):
	''' 
	Calculates distance between two XPath nodes
	
	Distance between /div/p[1] and /div/p[1] is 0
	Distance between /div/p[1] and /div/p[2] is 1
	'''

	def ignore(tag):
		number = tag.find('[')
		if number != -1:
			tag = tag[:number]
		return tag in ignored_tags

	def tail_weight(tail):
		tail_weight = 0
		for item in tail:
			index = xpath_index.search(item)
			tail_weight += (not index and 1 or int(index.group(1)) + 1)
		return tail_weight

	path_a = [ item for item in xpath_a.split('/') if item ]
	path_b = [ item for item in xpath_b.split('/') if item ]

	while ignore(path_a[-1]):
		path_a.pop()

	while ignore(path_b[-1]):
		path_b.pop()

#	print '1:', path_a
#	print '2:', path_b

	for i in xrange(min(len(path_a), len(path_b))):
		if path_a[i] != path_b[i]:
			break
		else:
			common_path = i + 1

#	print common_path

	tail_a = [ item for item in path_a[common_path:] if not ignore(item) ]
	tail_b = [ item for item in path_b[common_path:] if not ignore(item) ]

#	print tail_a
#	print tail_b

	tail_a_weight = tail_weight(tail_a)
	tail_b_weight = tail_weight(tail_b)

#	print 'tail_a weight:', tail_a_weight
#	print 'tail_b weight:', tail_b_weight

	return abs(tail_a_weight - tail_b_weight)


class RankException(Exception):
	pass


def rank(distance):
	'''Return rank from 1 to 10 based on XPath distance
	
	Distance 0 is rank 10
	Distance 1 is rank 9
	Distance more than (or equal to) 10 is rank 1
	'''
	if distance < 0:
		raise RankException('the fuck?')
	
	return min(10, max(11 - distance, 1))

if __name__ == '__main__':
	import unittest

	class DistanceTest(unittest.TestCase):
		distances = [
			('/div/p[0]', '/div/p[0]', 0), 
			('/div/p[0]', '/div/p[1]', 1), 
			('/div/p[0]', '/div/p[2]', 2), 
			('/div/p[1]', '/div/p[2]', 1), 
			('/div/p[1]', '/div/p[1]/p[0]', 1), 
			('/div', '/div/p[0]', 1), 
			('/div', '/div/p[1]', 2), 
			('/div', '/div/p[1]/p[0]', 3), 
			('/div', '/div/p[1]/p[2]', 5), 
		]

		def testDistance(self):
			for a, b, correct_distance in self.distances:
				assert(xpath_distance(a, b) == correct_distance)

		def testRank(self):
			assert(rank(0) == 10)
			assert(rank(1) == 10)
			assert(rank(10) == 1)
			assert(rank(11) == 1)
			assert(rank(100) == 1)
			
			try:
				rank(-1)
				self.fail('Expected RankException')
			except RankException:
				pass
			
			try:
				rank(-100)
				self.fail('Expected RankException')
			except RankException:
				pass

	unittest.main()
