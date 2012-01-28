#-*- coding: UTF-8

import ident.config
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

# this should be greed about second part (as in "Нижний Новгород"), so names
# like "Владимир Путин" will be fully consumed and "Владимир" won't hit geo db
city_finder = re.compile(
	ur'(%s)(\s+%s)?' % (location_name_pattern, location_name_pattern, )
	, re.UNICODE)


def geo_key(word):
	'''Covert word to shelve key as created by makedb.py'''
	return word.upper().replace(u'Ё', u'Е').encode(
		ident.config.geo_db.get('encoding', 'UTF-16'))


def geo_value(value):
	'''Convert shelve value back to Python (unicode) object'''
	return unicode(value.decode(
		ident.config.geo_db.get('encoding', 'UTF-16')))


def discard_candidate(plain_text, candidate, start_pos):
#	print plain_text, candidate, start_pos

	# ignore candidates at the beginning of the text
	# case: Московский комитет...
	if start_pos == 0:
		return True

	# ignore candidates at the beginning of the phrase
	match = re.match(ur'''.*[,.!?\-\—;:"'`()\[\]]\s*(%s)''' % candidate, plain_text)
	if match:
		return True


def cities(plain_text):
	'''Extract cities'''

	candidates = city_finder.finditer(plain_text)
	if not candidates:
		return []

	result = []
	for match_object in candidates:
		candidate = (match_object.group(0).strip())

		if discard_candidate(plain_text, candidate, match_object.start(0)):
#			print 'discarding', candidate
			continue

		key = geo_key(candidate)

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

	for city in cities(plain_text):
		key = geo_key(city)
		region = db.world.get(r'cit-%r' % (key, ), None)

		if region:
				result.append(geo_value(region).upper())

	return list(set(result))


if __name__ == '__main__':
	import unittest

	class GeoTest(unittest.TestCase):

		def testCities(self):
			testcases = (
				(u'Пиотровский предрек Санкт-Петербургу путь Венеции', u'Санкт-Петербург'),
				(u'рейсы в компоновке салонов экономического класса из Москвы по 14 направлениям', u'Москва'),
				(u'суд Нижнего Новгорода отказался удовлетворить иск группы нижегородцев', u'Нижний Новгород'),
				(u'Так, на участках Санкт-Петербург - Москва (по которым курсируют', u'Санкт-Петербург'),
			)

			for testcase, expected in testcases:
				assert(expected.upper() in cities(testcase))

		def testRegions(self):
			testcases = (
				(u'Пиотровский предрек Санкт-Петербургу путь Венеции', u'Санкт-Петербург'),
				(u'который пролегает от 14 микрорайона города Зеленограда до станции метро "Митино"', u'Москва'),
				(u'в суд обратились две воинские части МВД, расположенные в Приморском крае: во Владивостоке и селе Чугуевка', u'Приморский край'),
				(u'во Владивостоке и селе Чугуевка', u'Приморский край'),
			)

			for testcase, expected in testcases:
				assert(expected.upper() in regions(testcase))

		def testMisoperations(self):
			testcases = (
#				u'Московский комитет по культурному наследию', # Московский, Московская область
				u'Владимир Путин',  # Владимир, Владимирская область
				u'Путин Владимир',  # Владимир, Владимирская область
				u'В РОТ Фронт. — Московский комсомолец',  # Московский, Московская область
				u'Как сообщается в публикации "Московского комсомольца"',
				u'в этом году сообщали банк "Открытие", Московский банк реконструкции'
			)

			for testcase in testcases:
				assert(len(cities(testcase)) == 0)

	unittest.main()
