#-*- coding: UTF-8

import config
import re
import shelve


class DB(object):
	
	def __init__(self):
		self.cities = shelve.open(
			config.geo_db.get('cities', 'cities_ru/db/cities.shelve'))
		self.regions = shelve.open(
			config.geo_db.get('regions', 'cities_ru/db/regions.shelve'))
		self.world = shelve.open(
			config.geo_db.get('world', 'cities_ru/db/world.shelve'))


db = DB()
finder = re.compile(ur'([А-ЯЁ][а-яёА-ЯЁ\-]+)', re.UNICODE)


def geo_key(word):
	'''Covert word to shelve key as created by makedb.py'''
	return word.upper().replace(u'Ё', u'Е').encode(
		config.geo_db.get('encoding', 'UTF-16'))


def geo_value(value):
	'''Convert shelve value back to Python (unicode) object'''
	return unicode(value.decode(
		config.geo_db.get('encoding', 'UTF-16')))


def cities(plain_text):
	'''Extract cities'''
	
	candidates = finder.findall(plain_text)
	if not candidates:
		return []
	
	result = []
	for candidate in candidates:
		key = geo_key(candidate)
		
		if key in db.cities.iterkeys():
			result.append(geo_value(db.cities[key]))
	
	return list(set(result))


def regions(plain_text):
	'''
	Extract regions.
	Also do lookup for city's region if found any in plain_text.
	'''
	
	candidates = finder.findall(plain_text)
	if not candidates:
		return []
	
	result = []
	for candidate in candidates:
		key = geo_key(candidate)
		
		if key in db.cities.iterkeys():
			city = db.cities[key]
			region = db.world.get(r'cit-%r' % (city, ), None)
			
			if region:
				result.append(geo_value(region))
		
		if key in db.regions.iterkeys():
			result.append(geo_value(db.regions[key]))
	
	return list(set(result))


if __name__ == '__main__':
	import unittest
	
	class GeoTest(unittest.TestCase):
		
		def testCities(self):
			testcases = (
				(u'Пиотровский предрек Санкт-Петербургу путь Венеции', u'Санкт-Петербург'),
			)
			
			for testcase, expected in testcases:
				assert(expected.upper() in cities(testcase))
		
		def testRegions(self):
			testcases = (
				(u'Пиотровский предрек Санкт-Петербургу путь Венеции', u'Санкт-Петербург'),
				(u'который пролегает от 14 микрорайона города Зеленограда до станции метро "Митино"', u'Москва'),
				(u'Сначала он станцевал с делегацией из Чувашии', u'Чувашия'),
			)
			
			for testcase, expected in testcases:
				assert(expected.upper() in regions(testcase))
	
	
	unittest.main()
