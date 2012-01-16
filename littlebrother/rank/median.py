#-*- coding: UTF-8

# freqs: *ordered* *list* of (number, frequency) pairs
# e.g. ((2, 3), (3, 4),)
# where 2 is a number, 3 is a frequency of 2, 3 is a number, 4 is a frequency of 3


def median(freqs):
	"""Median from list of numbers and their frequencies"""

	samples = 0

	for (number, freq) in freqs:
		samples += freq

	samples_median = samples / 2.0

	current_samples = 0
	for (number, freq) in freqs:
		current_samples += freq
		if current_samples >= samples_median:
			return number

	return 0


if __name__ == '__main__':
	import unittest

	class MedianTest(unittest.TestCase):

		def testIt(self):
			assert(median(((2, 3),)) == 2.0)
			assert(median(((2, 3), (3, 3),)) == 2)
			assert(median(((7, 1), (8, 1), (9, 1),)) == 8)
			assert(median(((-1, 1), (1, 1),)) == -1)
			assert(median(((-1, 1), (-2, 1),)) == -1)
			assert(median(((7, 1),)) == 7)

	unittest.main()
