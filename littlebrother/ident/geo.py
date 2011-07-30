#-*- coding: UTF-8

import ident.config
import itertools
import re
import shelve


class DB(object):
	
	def __init__(self):
		self.cities = shelve.open(
			ident.config.geo_db.get('cities', 'cities_ru/db/cities.shelve')
			, flag = 'r')
		self.regions = shelve.open(
			ident.config.geo_db.get('regions', 'cities_ru/db/regions.shelve')
			, flag = 'r')
		self.world = shelve.open(
			ident.config.geo_db.get('world', 'cities_ru/db/world.shelve')
			, flag = 'r')


db = DB()

location_name_pattern = ur'[А-ЯЁ][а-яёА-ЯЁ\-]+' 
city_finder = re.compile(
	ur'(%s)(\s+%s)?' % (location_name_pattern, location_name_pattern, )
	, re.UNICODE)

simple_region_finder = re.compile(
	ur'(%s)' % (location_name_pattern, )
	, re.UNICODE)

composite_region_finder = re.compile(
	ur'(%s\s+[а-яё\-]+)' % (location_name_pattern, )
	, re.UNICODE)


def geo_key(word):
	'''Covert word to shelve key as created by makedb.py'''
	return word.upper().replace(u'Ё', u'Е').encode(
		ident.config.geo_db.get('encoding', 'UTF-16'))


def geo_value(value):
	'''Convert shelve value back to Python (unicode) object'''
	return unicode(value.decode(
		ident.config.geo_db.get('encoding', 'UTF-16')))


def cities(plain_text):
	'''Extract cities'''
	
	candidates = city_finder.findall(plain_text)
	if not candidates:
		return []
	
	result = []
	for head, tail in candidates:
		key = geo_key(u' '.join((head.strip(), tail.strip(), )).strip())
		
		if key in db.cities:
			value = geo_value(db.cities[key])
			result.append(value)
	
	return list(set(result))


def regions(plain_text):
	'''
	Extract regions.
	Also do lookup for city's region if found any in plain_text.
	'''
	
	result = []
	text = plain_text[:] # FIXME: not sure about memory copying
	
	# search for regions first
	# if any - remove it from text to exclude misoperations during cities search
	
	simple_candidates = simple_region_finder.findall(text)
	composite_candidates = composite_region_finder.findall(text)
	
	if simple_candidates or composite_candidates:
		for candidate in itertools.chain(simple_candidates, composite_candidates):
			key = geo_key(candidate.strip())
			
			if key in db.regions:
				value = geo_value(db.regions[key])
				text = text.replace(candidate, '')
				result.append(value)
	
	found_cities = cities(text)
	for city in found_cities:
		key = geo_key(city)
		region = db.world.get(r'cit-%r' % (key, ), None)
		
		if region:
				result.append(geo_value(region))
	
	return list(set(result))


if __name__ == '__main__':
	import unittest
	
	class GeoTest(unittest.TestCase):
		
		def testCities(self):
			testcases = (
				(u'Пиотровский предрек Санкт-Петербургу путь Венеции', u'Санкт-Петербург'),
				(u'рейсы в компоновке салонов экономического класса из Москвы по 14 направлениям', u'Москва'),
				(u'суд Нижнего Новгорода отказался удовлетворить иск группы нижегородцев', u'Нижний Новгород'),
				(u'Так, на участках Санкт-Петербург - Москва (по которым курсируют', u'Москва'),
				(u'Так, на участках Санкт-Петербург - Москва (по которым курсируют', u'Санкт-Петербург'),
			)
			
			for testcase, expected in testcases:
				assert(expected.upper() in cities(testcase))
		
		def testRegions(self):
			testcases = (
				(u'Пиотровский предрек Санкт-Петербургу путь Венеции', u'Санкт-Петербург'),
				(u'который пролегает от 14 микрорайона города Зеленограда до станции метро "Митино"', u'Москва'),
				(u'Сначала он станцевал с делегацией из Чувашии', u'Чувашия'),
				(u'Фото с сайта УФМС России по Приморскому краю', u'Приморский край'),
				(u'в суд обратились две воинские части МВД, расположенные в Приморском крае: во Владивостоке и селе Чугуевка', u'Приморский край'),
				(u'во Владивостоке и селе Чугуевка', u'Приморский край'),
			)
			
			for testcase, expected in testcases:
				assert(expected.upper() in regions(testcase))
	
	
	unittest.main()
