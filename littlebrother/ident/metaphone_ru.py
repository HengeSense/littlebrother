#-*- coding: UTF-8

# http://forum.aeroion.ru/topic461.html

import re

# Гласные
vowels_replace = (
	(re.compile(ur'([ОЫАЯ])', re.UNICODE), ur'А'), 
	(re.compile(ur'([ЮУ])', re.UNICODE), ur'У'), 
	(re.compile(ur'([ЕЁЭИЙ]|ЙО|ЙЕ)', re.UNICODE), ur'И'), 
	)

# Оглушение согласных в слабой позиции
consonants = u'БВГДЖЗКЛМНПРСТФХЦЧШЩ'

consonants_replace = (
	(re.compile(ur'(Б)([%s\s]|\b)' % consonants, re.UNICODE), ur'П\2'), 
	(re.compile(ur'(З)([%s\s]|\b)' % consonants, re.UNICODE), ur'С\2'), 
	(re.compile(ur'(Д)([%s\s]|\b)' % consonants, re.UNICODE), ur'Т\2'), 
	(re.compile(ur'(В)([%s\s]|\b)' % consonants, re.UNICODE), ur'Ф\2'), 
	(re.compile(ur'(Г)([%s\s]|\b)' % consonants, re.UNICODE), ur'К\2'), 
	)

# Сжатие окончаний
endings_replace = (
	(re.compile(ur'(УК|ЮК)$', re.UNICODE), ur'0'),
	(re.compile(ur'(ЕН|ЕНА|ИН|ИНА)$', re.UNICODE), ur'1'), 
	(re.compile(ur'(ИК|ЕК)$', re.UNICODE), ur'2'), 
	(re.compile(ur'(КО)$', re.UNICODE), ur'3'), # was 'НКО' in original 
	(re.compile(ur'(ОВ|ЕВ|ИЕВ|ЕЕВ|ОВА|ЕВА|ИЕВА|ЕЕВА)$', re.UNICODE), ur'4'), 
	(re.compile(ur'(ЫХ|ИХ)$', re.UNICODE), ur'5'), 
	(re.compile(ur'(ИЙ|ЫЙ|АЯ)$', re.UNICODE), ur'6'), 
	(re.compile(ur'(ОВСКИЙ|ЕВСКИЙ|ОВСКАЯ|ЕВСКАЯ)$', re.UNICODE), ur'7'), 
	(re.compile(ur'(АН|ЯН|АНЦ|УНЦ|ЕНЦ)$', re.UNICODE), ur'8'),
	(re.compile(ur'(ИЧ)$', re.UNICODE), ur'9'),  
	)

# Исключение повторяющихся символов
doubles_replace = (re.compile(ur'(.)\1+', re.UNICODE), ur'\1')

# Исключение Ъ, Ь и дефиса между частями двойной фамилии
misspelling_replace = (re.compile(ur'([ЪЬ-])', re.UNICODE), u'')


def metaphone(text):
	"""Ожидает text в верхнем регистре"""

	def apply_regexps(text, regexps, to_first_successfull = False):
		out = text
		for regex, replacement in regexps:
			out, replacements = regex.subn(replacement, out)
			if to_first_successfull and replacements > 0:
				break
		return out

	def preprocess(text):
		'''
		1) Исключение повторяющихся символов
		2) Исключение Ъ, Ь и дефиса между частями двойной фамилии
		3) Сжатие окончаний
		'''
		return apply_regexps(apply_regexps(text, (doubles_replace, misspelling_replace, )), 
			endings_replace, to_first_successfull = True)

	def process(text):
		'''
		1) Гласные
		2) Оглушение согласных в слабой позиции
		'''
		return apply_regexps(text, vowels_replace + consonants_replace)

	def postprocess(text):
		'''
		1) Исключение повторяющихся символов
		'''
		return apply_regexps(text, (doubles_replace, ))


	return postprocess(process(preprocess(text)))


if __name__ == '__main__':
	# performance test
	import sys
	import time
	
	samples = 10000
	start = time.time()
	for i in xrange(samples):
		metaphone(u'БАУЭР')
	stop = time.time()

	diff = stop - start
	print >> sys.stderr, samples / diff, 'samples per second'

	# unittests
	import unittest

	class MetaphoneRuTest(unittest.TestCase):
		
		def testVowels(self):
			assert(metaphone(u'БАУЭР') == metaphone(u'БАУЕР') == u'БАУИР')
			assert(metaphone(u'ЗИЦЕР') == metaphone(u'ЗИЦИР') == u'ЗИЦИР')
		
		def testConsonants(self):
			assert(metaphone(u'ЛАГ') == metaphone(u'ЛАК') == u'ЛАК')
			assert(metaphone(u'ГУДЗ') == metaphone(u'ГУТС') == u'ГУТС')
			# В оригинале ожидается 'ГЕФТ', но Е -> И
			assert(metaphone(u'ГЕФТ') == metaphone(u'ГЕВТ') == u'ГИФТ')
			# В оригинале ожидается 'БОФТ', но А -> О
			assert(metaphone(u'БОВТ') == metaphone(u'БОФТ') == u'БАФТ')
		
		def testDoubles(self):
			assert(metaphone(u'БОПП') == metaphone(u'БОП') == u'БАП')
			assert(metaphone(u'МЕТРЕВЕЛИ') == metaphone(u'МЕТРЕВЕЛЛИ') == u'МИТРИВИЛИ')
			assert(metaphone(u'ШМИДТ') == metaphone(u'ШМИТ') == u'ШМИТ')
		
		def testEndings(self): # includes misspelling test
			assert(metaphone(u'ОГОЛЬЦОВА') == metaphone(u'АГАЛЬЦОВА') == u'АГАЛЦ4')
			# В оригинале ожидается 'ГРИЦ', но Г -> К
			assert(metaphone(u'ГРИЦЮК') == metaphone(u'ГРИЦУК') == u'КРИЦ0')

	unittest.main()
