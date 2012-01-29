#-*- coding: UTF-8

from sqlalchemy import func  # FIXME: this belongs to db.sqldb somehow
from sqlalchemy import not_  # FIXME: this belongs to db.sqldb somehow
import api.config
import api.utils
import db.database
import db.sqldb
import ident.metaphone_ru
import itertools
import re


MAX_IDENTS = api.config.api.get('max_idens', 5)
MAX_CONNECTIONS = api.config.api.get('max_connections', 15)
MAX_TAGS = api.config.api.get('max_tags', 10)
MAX_INTERSECTION_IDENTS = api.config.api.get('max_intersection_idents', 3)
MAX_URLS = api.config.api.get('max_urls', 15)
MAX_CONNECTIONS_FILTER_TOKENS = api.config.api.get('max_connections_filter_tokens', 2)
MAX_URLS_FILTER_TOKENS = api.config.api.get('max_title_filter_tokens', 5)
MAX_PACK_LAYER1_SIZE = api.config.api.get('max_pack_layer_1_size', 15)
MAX_PACK_LAYER2_SIZE = api.config.api.get('max_pack_layer_2_size', 30)

IO_ENCODING = api.config.api.get('encoding', 'UTF-8')
NAME_FROM_URL_REGEX = re.compile(ur'(.*):(.*)', re.IGNORECASE | re.UNICODE)


class QueryError(Exception):
	pass


def name_from_url(string):
	result = NAME_FROM_URL_REGEX.search(string)
	if result:
		return { 'title' : result.group(1), 'tag' : result.group(2) }


def get_ident(database, title, tag):
	return database.query(db.sqldb.Ident)\
		.filter(db.sqldb.Ident.title == title)\
		.filter(db.sqldb.Ident.tag == tag)\
		.one()


def idents(frontend, args):
	'''
	List identities according to pattern
	Arguments: pattern -> string, offset - > int
	'''

	try:
		pattern = args.get('pattern', [None])[0]
		tags = args.get('tags', [])
		offset = int(args.get('offset', ['0'])[0])
		limit = int(args.get('limit', ['0'])[0])
	except Exception, e:
		raise QueryError('Invalid argument: ' + str(e))

	if not limit:
		limit = MAX_IDENTS

	limit = min(limit, MAX_IDENTS)

	if not pattern:
		raise QueryError("Invalid argument: 'pattern' can't be empty")

	valid_pattern = (pattern
		and api.utils.sql_escape(pattern.decode(IO_ENCODING))
		or None)

	if not api.utils.sql_valid(valid_pattern):
		raise QueryError('Invalid argument: ' + pattern)

	if len(tags) > MAX_TAGS:
		raise QueryError("Invalid argument: 'tags' list should include not more than " + MAX_TAGS + " entries")

	valid_tags = [ api.utils.sql_escape(tag) for tag in tags ]
	for tag, original_tag in zip(valid_tags, tags):
		if not tag or not api.utils.sql_valid(tag):
			raise QueryError('Invalid argument: ' + original_tag)

	database = db.database.get_frontend_db_ro()

	db_idents = database.query(db.sqldb.Ident)\
		.filter(db.sqldb.Ident.title.like(valid_pattern + '%'))

	if valid_tags:
		db_idents = db_idents\
			.filter(db.sqldb.Ident.tag.in_(valid_tags))

	db_idents = db_idents\
		.order_by(db.sqldb.Ident.score.desc())\
		.offset(offset)\
		.limit(limit)

	return frontend((
		{
			'title' : ident.title,
			'tag' : ident.tag,
			'score' : ident.score,
		}
		for ident in db_idents
	))


def fuzzy_idents(frontend, args):
	'''
	List identities similar to pattern
	Arguments: pattern -> string, offset - > int
	'''

	try:
		pattern = args.get('pattern', [None])[0]
		offset = int(args.get('offset', ['0'])[0])
		limit = int(args.get('limit', ['0'])[0])
	except Exception, e:
		raise QueryError('Invalid argument: ' + str(e))

	if not limit:
		limit = MAX_IDENTS

	limit = min(limit, MAX_IDENTS)

	if not pattern:
		raise QueryError("Invalid argument: 'pattern' can't be empty")

	valid_pattern = (pattern
		and api.utils.sql_escape(pattern.decode(IO_ENCODING))
		or None)

	if not api.utils.sql_valid(valid_pattern):
		raise QueryError('Invalid argument: ' + pattern)

	metaphone = ident.metaphone_ru.metaphone(valid_pattern)

	database = db.database.get_frontend_db_ro()

	db_idents = database.query(db.sqldb.Ident)\
		.filter(db.sqldb.Ident.metaphone.like(metaphone + '%'))\
		.order_by(db.sqldb.Ident.score.desc())\
		.offset(offset)\
		.limit(limit)

	return frontend((
		{
			'title' : ident.title,
			'tag' : ident.tag,
			'score' : ident.score,
		}
		for ident in db_idents
	))


def connections(frontend, args):
	'''
	List identities connections (according to pattern and tag if any)
	Arguments: idents -> string list, offset - > int, tags -> string list, pattern -> string
	'''

	try:
		idents = args.get('idents', [])
		offset = int(args.get('offset', ['0'])[0])
		limit = int(args.get('limit', ['0'])[0])
		tags = args.get('tags', [])
		pattern = args.get('pattern', [None])[0]
	except Exception, e:
		raise QueryError('Invalid argument: ' + str(e))

	if not limit:
		limit = MAX_CONNECTIONS

	limit = min(limit, MAX_CONNECTIONS)

	if not idents:
		raise QueryError("Invalid argument: 'idents' list can not be empty")

	valid_pattern = (pattern and api.utils.sql_escape(pattern.decode(IO_ENCODING)) or None)
	if pattern:
		if not api.utils.sql_valid(valid_pattern):
			raise QueryError('Invalid argument: ' + pattern)

	if len(idents) > MAX_INTERSECTION_IDENTS:
		raise QueryError("Invalid argument: 'idents' list must include not more than " + str(MAX_INTERSECTION_IDENTS) + " entries")

	valid_idents = [ name_from_url(api.utils.sql_escape(ident.decode(IO_ENCODING))) for ident in idents ]
	for ident, original_ident in zip(valid_idents, idents):
		if not ident:
			raise QueryError("Invalid argument: " + str(original_ident))

		if not api.utils.sql_valid(ident.get('title', u'')) or not api.utils.sql_valid(ident.get('tag', u'')):
			raise QueryError('Invalid argument: ' + ident)

	if len(tags) > MAX_TAGS:
		raise QueryError("Invalid argument: 'tags' list should include not more than " + MAX_TAGS + " entries")

	valid_tags = [ api.utils.sql_escape(tag.decode(IO_ENCODING)) for tag in tags ]
	for tag, original_tag in zip(valid_tags, tags):
		if not tag or not api.utils.sql_valid(tag):
			raise QueryError('Invalid argument: ' + original_tag)

	database = db.database.get_frontend_db_ro()

	db_idents = [ get_ident(database, ident.get('title', u''), ident.get('tag', u'')) for ident in valid_idents ]

	if (len(db_idents) != len(valid_idents)):
		invalid_idents = ( ident.encode(IO_ENCODING) for ident in valid_idents if ident not in ( ident.title for ident in db_idents ) )
		raise QueryError('Invalid argument(s): ' + ', '.join(invalid_idents))

	max_score = func.max(db.sqldb.Friend.score)

	db_connections = database.query(db.sqldb.Friend.ident_2_id, max_score)\
		.filter(db.sqldb.Friend.ident_1_id.in_((ident.id for ident in db_idents)))\
		.group_by(db.sqldb.Friend.ident_2_id)\
		.having(func.count(db.sqldb.Friend.ident_2_id) == len(db_idents))\
		.order_by(max_score.desc())

	if valid_tags:
		db_connections = db_connections\
			.filter(db.sqldb.Friend.ident_2_tag.in_(valid_tags))

	if pattern:
		max_tokens = MAX_CONNECTIONS_FILTER_TOKENS
		for token in valid_pattern.split(' ')[:max_tokens]:
			db_connections = db_connections\
				.filter(db.sqldb.Friend.ident_2_title.op('ilike')('%' + token.strip() + '%'))

	db_connections = db_connections\
		.offset(offset)\
		.limit(limit)

	connections_ids = ( connection.ident_2_id for connection in db_connections )

	result = database.query(db.sqldb.Friend)\
		.filter(db.sqldb.Friend.ident_1_id == db_idents[0].id)\
		.filter(db.sqldb.Friend.ident_2_id.in_(connections_ids))\
		.order_by(db.sqldb.Friend.score.desc())

	return frontend((
		{
			'title' : connection.ident_2_title.encode(IO_ENCODING),
			'tag' : connection.ident_2_tag,
			'median' : connection.median,
			'average' : connection.average,
			'score' : connection.score,
		}
		for connection in result
	))


def urls(frontend, args):
	'''
	List identities mentions (according to title and domain if any)
	Arguments: idents -> string list, offset - > int, title -> string, domain -> string
	'''

	try:
		idents = args.get('idents', [])
		offset = int(args.get('offset', ['0'])[0])
		limit = int(args.get('limit', ['0'])[0])
		title = args.get('title', [None])[0]
		domain = args.get('domain', [None])[0]
	except Exception, e:
		raise QueryError('Invalid argument: ' + str(e))

	if not limit:
		limit = MAX_URLS

	limit = min(limit, MAX_URLS)

	if not idents:
		raise QueryError("Invalid argument: 'idents' list can not be empty")

	valid_title = (title and api.utils.sql_escape(title.decode(IO_ENCODING)) or None)
	if title:
		if not api.utils.sql_valid(valid_title):
			raise QueryError('Invalid argument: ' + title)

	valid_domain = (domain and api.utils.sql_escape(domain.decode(IO_ENCODING)) or None)
	if domain:
		if not api.utils.sql_valid(valid_domain):
			raise QueryError('Invalid argument: ' + domain)

	if len(idents) > MAX_INTERSECTION_IDENTS:
		raise QueryError("Invalid argument: 'idents' list must include not more than " + str(MAX_INTERSECTION_IDENTS) + " entries")

	valid_idents = [ name_from_url(api.utils.sql_escape(ident.decode(IO_ENCODING))) for ident in idents ]
	for ident, original_ident in zip(valid_idents, idents):
		if not ident:
			raise QueryError("Invalid argument: " + str(original_ident))

		if not api.utils.sql_valid(ident.get('title', u'')) or not api.utils.sql_valid(ident.get('tag', u'')):
			raise QueryError('Invalid argument: ' + ident)

	database = db.database.get_frontend_db_ro()

	db_idents = [ get_ident(database, ident.get('title', u''), ident.get('tag', u'')) for ident in valid_idents ]

	if (len(db_idents) != len(valid_idents)):
		invalid_idents = ( ident.encode(IO_ENCODING) for ident in valid_idents if ident not in ( ident.title for ident in db_idents ) )
		raise QueryError('Invalid argument(s): ' + ', '.join(invalid_idents))

	db_web = database.query(db.sqldb.Web.url_id)\
		.filter(db.sqldb.Web.ident_id.in_(( ident.id for ident in db_idents )))\
		.group_by(db.sqldb.Web.url_id)\
		.having(func.count(db.sqldb.Web.url_id) == len(db_idents))

	if title:
		max_tokens = MAX_URLS_FILTER_TOKENS
		for token in valid_title.split(' ')[:max_tokens]:
			db_web = db_web.filter(db.sqldb.Web.url_title.op('ilike')('%' + token.strip() + '%'))

	if domain:
		db_web = db_web.filter(db.sqldb.Web.url_ref.op('ilike')('%' + valid_domain + '%'))

	db_web = db_web\
		.order_by(db.sqldb.Web.url_id)\
		.offset(offset)\
		.limit(limit)

	url_ids = ( web.url_id for web in db_web )

	result = database.query(db.sqldb.Web)\
		.filter(db.sqldb.Web.ident_id == db_idents[0].id)\
		.filter(db.sqldb.Web.url_id.in_(url_ids))\
		.order_by(db.sqldb.Web.url_id)

	return frontend((
		{
			'ref' : web.url_ref,
			'ref_title' : web.url_title,
		}
		for web in result
	))


def pack(frontend, args):
	'''
	List identities pack
	Arguments: ident -> string, tags - > string list, level_1_offset -> int, level_2_offset -> int, pattern -> string
	'''

	try:
		idents = args.get('idents', [])
		tags = args.get('tags', [])
		offset = int(args.get('offset', ['0'])[0])
		pattern = args.get('pattern', [None])[0]
	except Exception, e:
		raise QueryError('Invalid argument: ' + str(e))

	if not idents or not idents[0]:
		raise QueryError("Invalid argument: 'idents' can not be empty")

	if len(idents) != 1:
		raise QueryError("Invalid argument: len of 'idents' can not be greater than 1 person")

	valid_ident = name_from_url(api.utils.sql_escape(idents[0].decode(IO_ENCODING)))
	if not valid_ident \
	or not api.utils.sql_valid(valid_ident.get('title', u'')) \
	or not api.utils.sql_valid(valid_ident.get('tag', u'')):
		raise QueryError('Invalid argument: ' + ident)

	if len(tags) > MAX_TAGS:
		raise QueryError("Invalid argument: 'tags' list should include not more than " + MAX_TAGS + " entries")

	valid_tags = [ api.utils.sql_escape(tag.decode(IO_ENCODING)) for tag in tags ]
	for tag, original_tag in zip(valid_tags, tags):
		if not tag or not api.utils.sql_valid(tag):
			raise QueryError('Invalid argument: ' + original_tag)

	valid_pattern = (pattern and api.utils.sql_escape(pattern.decode(IO_ENCODING)) or None)
	if pattern:
		if not api.utils.sql_valid(valid_pattern):
			raise QueryError('Invalid argument: ' + pattern)

	database = db.database.get_frontend_db_ro()

	db_ident = get_ident(database, valid_ident.get('title', u''), valid_ident.get('tag', u''))

	if not db_ident:
		raise QueryError('Invalid argument: ' + ident)

	max_score = func.max(db.sqldb.Friend.score)

	# level 1
	db_connections_lv1 = database.query(db.sqldb.Friend.ident_2_id)\
		.filter(db.sqldb.Friend.ident_1_id == db_ident.id)\
		.order_by(db.sqldb.Friend.score.desc())

	if valid_tags:
		db_connections_lv1 = db_connections_lv1\
			.filter(db.sqldb.Friend.ident_2_tag.in_(valid_tags))

	if pattern:
		max_tokens = MAX_CONNECTIONS_FILTER_TOKENS
		for token in valid_pattern.split(' ')[:max_tokens]:
			db_connections_lv1 = db_connections_lv1\
				.filter(db.sqldb.Friend.ident_2_title.op('ilike')('%' + token.strip() + '%'))

	db_connections_lv1 = db_connections_lv1\
		.offset(offset)\
		.limit(MAX_PACK_LAYER1_SIZE)

	lv1_ids = [ connection.ident_2_id for connection in db_connections_lv1 ]
	lv2_ids = []

	if lv1_ids:
		# level 2
		db_connections_lv2 = database.query(db.sqldb.Friend.ident_2_id, max_score)\
			.filter(db.sqldb.Friend.ident_1_id.in_(lv1_ids))\
			.filter(not_(db.sqldb.Friend.ident_2_id.in_(itertools.chain(lv1_ids, (db_ident.id, )))))\
			.group_by(db.sqldb.Friend.ident_2_id)\
			.order_by(max_score.desc())

		if valid_tags:
			db_connections_lv2 = db_connections_lv2\
				.filter(db.sqldb.Friend.ident_2_tag.in_(valid_tags))

		db_connections_lv2 = db_connections_lv2\
			.limit(MAX_PACK_LAYER2_SIZE)

		lv2_ids = [ connection.ident_2_id for connection in db_connections_lv2 ]

	db_connections = database.query(db.sqldb.Ident)\
		.filter(db.sqldb.Ident.id.in_(itertools.chain(lv1_ids, lv2_ids)))

	return frontend((
		{
			'title' : ident.title.encode(IO_ENCODING),
			'tag' : ident.tag,
			'score' : ident.score,
			'level' : ident.id in lv2_ids and 2 or 1,
		}
		for ident in db_connections
	))


def stats(frontend, args):
	'''List DB statistics'''

	database = db.database.get_frontend_db_ro()

	db_stats = database.query(db.sqldb.Stat).all()

	stats = {}
	for db_stat in db_stats:
		stats[db_stat.key] = db_stat.value

	return frontend((stats, ))


if __name__ == '__main__':
	import unittest
	import jsonfront

	class QueryTest(unittest.TestCase):
		main_pattern = 'ПУТИН'
		main_ident = main_pattern + ' ВЛАДИМИР'
		secondary_ident = 'МЕДВЕДЕВ ДМИТРИЙ'
		idents_tag = 'names'
		idents = ( main_ident + ':names', secondary_ident + ':names', )
		ref = 'http://kremlin.ru'

		def setUp(self):
			database = db.database.get_frontend_db_rw()

			ident1 = database.query(db.sqldb.Ident)\
				.filter(db.sqldb.Ident.title == self.main_ident)\
				.first()
			if ident1 == None:
				ident1 = db.sqldb.Ident(self.main_ident, self.idents_tag)
				database.add(ident1)

			ident2 = database.query(db.sqldb.Ident)\
				.filter(db.sqldb.Ident.title == self.secondary_ident)\
				.first()
			if ident2 == None:
				ident2 = db.sqldb.Ident(self.secondary_ident, self.idents_tag)
				database.add(ident2)

			node = database.query(db.sqldb.Node)\
				.filter(db.sqldb.Node.ident_1_id == ident1.id)\
				.filter(db.sqldb.Node.ident_2_id == ident2.id)\
				.first()
			if node == None:
				url = database.query(db.sqldb.Url)\
					.filter(db.sqldb.Url.ref == self.ref)\
					.first()
				if url == None:
					url = db.sqldb.Url(self.ref, '')
					database.add(url)
					database.commit()

				node = db.sqldb.Node(ident1, ident2, url, 0)
				database.add(node)

			link = database.query(db.sqldb.Link)\
				.filter(db.sqldb.Link.ident_1_id == ident1.id)\
				.filter(db.sqldb.Link.ident_2_id == ident2.id)\
				.first()
			if link == None:
				link = db.sqldb.Link(ident1, ident2)
				database.add(link)

			database.commit()

		def checkResults(self, frontend):
			fulltext = ''
			for chunk in idents(frontend, { 'pattern' : [self.main_pattern], 'offset' : ['0'] }):
				fulltext += chunk
			assert(fulltext)
#			print fulltext

			fulltext = ''
			for chunk in urls(frontend, { 'idents' : self.idents, 'offset' : ['0'] }):
				fulltext += chunk
			assert(fulltext)
#			print fulltext

			fulltext = ''
			for chunk in connections(frontend, { 'idents' : [self.main_ident + ':' + self.idents_tag], 'offset' : ['0'] }):
				fulltext += chunk
			assert(fulltext)
#			print fulltext

		def testJson(self):
			self.checkResults(jsonfront.dump)

	class ErrorsTest(unittest.TestCase):

		def checkInvalidArgument(self, interface, args, argument_name):

			def stub_frontend(*args):
				return ''

			try:
				interface(stub_frontend, args)
			except QueryError, e:
#				print e
				assert('Invalid argument' in str(e) and argument_name in str(e))

		def testIdents(self):
			self.checkInvalidArgument(idents, {}, 'pattern')
			self.checkInvalidArgument(idents, {
				'pattern' : ['']
				}, 'pattern')
			self.checkInvalidArgument(idents, {
				'pattern' : ['x'],
				'offset' : ['x'],
				}, 'int()')
			self.checkInvalidArgument(idents, {
				'pattern' : ['x'],
				'offset' : ['0'],
				'limit' : ['x'],
				}, 'int()')

		def testFuzzyIdents(self):
			self.checkInvalidArgument(fuzzy_idents, {}, 'pattern')
			self.checkInvalidArgument(fuzzy_idents, {
				'pattern' : ['x'],
				'offset' : ['x'],
				}, 'int()')
			self.checkInvalidArgument(fuzzy_idents, {
				'pattern' : ['x'],
				'offset' : ['0'],
				'limit' : ['x'],
				}, 'int()')

		def testConnections(self):
			self.checkInvalidArgument(connections, {}, 'idents')
			self.checkInvalidArgument(connections, {
				'idents' : []
				}, 'idents')
			self.checkInvalidArgument(connections, {
				'idents' : ['x'],
				'offset' : ['x'],
				}, 'int()')
			self.checkInvalidArgument(connections, {
				'idents' : ['x'],
				'offset' : ['0'],
				'limit' : ['x'],
				}, 'int()')
			self.checkInvalidArgument(connections, {
				'idents' : ['x'] * (MAX_INTERSECTION_IDENTS + 1),
				'offset' : ['0'],
				'limit' : ['0'],
				}, 'idents')

		def testUrls(self):
			self.checkInvalidArgument(urls, {}, 'idents')
			self.checkInvalidArgument(urls, {
				'idents' : []
				}, 'idents')
			self.checkInvalidArgument(urls, {
				'idents' : ['x'],
				'offset' : ['x'],
				}, 'int()')
			self.checkInvalidArgument(urls, {
				'idents' : ['x'],
				'offset' : ['0'],
				'limit' : ['x'],
				}, 'int()')
			self.checkInvalidArgument(urls, {
				'idents' : ['x'] * (MAX_INTERSECTION_IDENTS + 1),
				'offset' : ['0'],
				'limit' : ['0'],
				}, 'idents')

		def testPack(self):
			self.checkInvalidArgument(pack, {}, 'idents')
			self.checkInvalidArgument(pack, {
				'idents' : []
				}, 'idents')
			self.checkInvalidArgument(fuzzy_idents, {
				'idents' : ['x'],
				'offset' : ['x'],
				}, 'int()')

	#TODO: test 'limit' handling
	#TODO: test aliases

	unittest.main()
