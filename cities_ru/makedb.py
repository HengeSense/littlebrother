#-*- coding: UTF-8

import adapter
import shelve
import sys

source_encoding = 'UTF-8'


def collect_cities(fp):
	regions = {}
	cities = set()
	
	for line in fp:
		city, region = line.decode(source_encoding).strip().split(',')
		if not region:
			region = city
		
		cities.add(city.strip())
		
		if region:
			region_cities = regions.get(region.strip(), set())
			region_cities.add(city.strip())
			regions[region.strip()] = region_cities
	
	return {
		'regions' : regions,
		'cities' : cities,
	}


def decline(geo):
	location = geo.upper().replace(u'Ё', u'Е')
	words = location.split(' ')
	
	declined = [ location ]
	for case in (u'рд', u'дт', u'вн', u'тв', u'пр', ):
		inflected_location = ' '.join(
			adapter.morph.inflect_ru(word, u'%s,ед' % (case, ))
			for word in words)
		declined.append(inflected_location)
#		print inflected_location
	
	return declined


def save_cities(cities, cities_db):
	d = shelve.open(cities_db)
	
	for city in cities:
		declined = decline(city)
		for case in declined:
			d[case.encode(adapter.db_encoding)] = declined[0].encode(adapter.db_encoding)
	
	d.close()


def save_regions(regions, regions_db):
	d = shelve.open(regions_db)
	
	regions_list = [ region for region in regions ]
	
	d['all'] = regions_list
	for region in regions_list:
		declined = decline(region)
		for case in declined:
			d[case.encode(adapter.db_encoding)] = declined[0].encode(adapter.db_encoding)
	
	d.close()


def save_world(world, world_db):
	
	def region_key(region):
		return r'reg-%r' % (region.upper().encode(adapter.db_encoding), )
	
	def city_key(city):
		return r'cit-%r' % (city.upper().encode(adapter.db_encoding), )
	
	d = shelve.open(world_db)
	
	for region, cities in world.iteritems():
		d[region_key(region)] = [
			city.upper().encode(adapter.db_encoding) 
			for city in cities ]
		
		for city in cities:
			d[city_key(city)] = region.upper().encode(adapter.db_encoding)
	
	d.close()


def usage(app):
	print 'usage: %s [FILENAME]' % (app, )


if __name__ == '__main__':
	if len(sys.argv) < 2:
		usage(sys.argv[0])
		sys.exit(1)
		
	cities_file = sys.argv[1]
	
	collected = collect_cities(open(cities_file, 'rt'))
	
	regions_map = collected.get('regions', {})
	regions = collected.get('regions', {}).iterkeys()
	cities = collected.get('cities', set())
	
	save_cities(cities, adapter.cities_db)
	save_regions(regions, adapter.regions_db)
	save_world(regions_map, adapter.world_db)
