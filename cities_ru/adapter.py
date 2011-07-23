#-*- coding: UTF-8

import littlebrother.ident.config as ident_config
import os.path
import pymorphy

db_encoding = ident_config.geo_db.get('encoding', 'UTF-16')
cities_db = ident_config.geo_db.get('cities', 'cities_ru/db/cities.shelve')
regions_db = ident_config.geo_db.get('regions', 'cities_ru/db/regions.shelve')
world_db = ident_config.geo_db.get('world', 'cities_ru/db/db/regions.shelve')

cities_db = os.path.join('..', cities_db)
regions_db = os.path.join('..', regions_db)
world_db = os.path.join('..', world_db)

morph = pymorphy.get_morph(
	os.path.join('..', ident_config.dicts.get('path', 'dicts/ru/shelve45')), 
	ident_config.dicts.get('backend', 'shelve'))

