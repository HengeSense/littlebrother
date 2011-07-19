#-*- coding: UTF-8

# freqs: list or generator of (number, frequency) pairs
# e.g. ((2, 3), (3, 4),)
# where 2 is a number, 3 is a frequency of 2, 3 is a number, 4 is a frequency of 3


def average(freqs):
	"""Average from list of numbers and their frequencies"""
	
	avg = 0.0
	samples = 0
	
	for (number, freq) in freqs:
		if freq > 0:
			avg = (avg * samples + number * freq) / (samples + freq)
			samples += freq
	
	return avg


if __name__ == '__main__':
	import unittest
	
	class AverageTest(unittest.TestCase):
		
		def testIt(self):
			assert(average(((2, 3),)) == 2.0)
			assert(average(((2, 3), (3, 3),)) == 2.5)
			assert(average(((7, 1), (8, 1), (9, 1),)) == 8)
			assert(average(((-1, 1), (1, 1),)) == 0)
			assert(average(((-1, 1), (-2, 1),)) == -1.5)

	unittest.main()
