#-*- coding: UTF-8


def next_weight(current_weight, samples_number, new_sample):
	"""Add number to average, given current average and samples number"""
	
	if samples_number <= 0:
		return new_sample
	
	return (current_weight + new_sample / float(samples_number)) / ((samples_number + 1) / float(samples_number))


def prev_weight(current_weight, samples_number, old_sample):
	"""Remove number from average, given current average and samples number"""
	
	if samples_number <= 1:
		return 0
	
	return (current_weight - old_sample / float(samples_number)) / ((samples_number - 1) / float(samples_number))


if __name__ == '__main__':
	import unittest
	
	class WeightTest(unittest.TestCase):
		
		def testNext(self):
			assert(next_weight(0, 0, 9) == 9.0)
			assert(next_weight(9, 0, 9) == 9.0)
			assert(next_weight(9, 1, 9) == 9.0)
			assert((11 + 10 + 9 + 8) / 4.0 == 
				next_weight(
					next_weight(
						next_weight(
							next_weight(0, 0, 8), 
						1, 9), 
					2, 10), 
				3, 11))
			
		def testPrev(self):
			assert(prev_weight(0, 0, 9) == 0.0)
			assert(prev_weight(9, 0, 9) == 0.0)
			assert(prev_weight(9, 1, 9) == 0.0)
			assert(prev_weight((10 + 9 + 8 + 7) / 4.0, 4, 8)
				== (10 + 9 + 7) / 3.0)
			
	unittest.main()
