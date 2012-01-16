#-*- coding: UTF-8

from sqlalchemy import func # FIXME: this belongs to db.sqldb somehow
from sqlalchemy import not_ # FIXME: this belongs to db.sqldb somehow
import api.config
import api.utils
import db.database
import db.sqldb
import ident.metaphone_ru
import itertools
import re


name_from_url_regex = re.compile(ur'(.*):(.*)', re.IGNORECASE | re.UNICODE)

class QueryError(Exception):
	pass

def name_from_url(string):
	result = name_from_url_regex.search(string)
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
		tag = args.get('tag', [None])[0]
		offset = int(args.get('offset', ['0'])[0])
		limit = int(args.get('limit', ['0'])[0])
	except Exception, e:
		raise QueryError('Invalid argument: ' + str(e))
	
	if not limit:
		limit = api.config.api.get('max_idents', 5)
		
	limit = min(limit, api.config.api.get('max_idents', 5))
	
	if not pattern:
		raise QueryError("Invalid argument: 'pattern' can't be empty")
	
	valid_pattern = (pattern 
		and api.utils.sql_escape(pattern.decode(api.config.api.get('encoding', 'UTF-8'))) 
		or None)
	
	if not api.utils.sql_valid(valid_pattern):
		raise QueryError('Invalid argument: ' + pattern)
	
	database = db.database.get_frontend_db_ro()
	
	db_idents = database.query(db.sqldb.Ident)\
		.filter(db.sqldb.Ident.title.like(valid_pattern + '%'));
		
	if tag:
		db_idents = db_idents\
			.filter(db.sqldb.Ident.tag == tag);
		
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
		limit = api.config.api.get('max_idents', 5)
	
	limit = min(limit, api.config.api.get('max_idents', 5))
	
	if not pattern:
		raise QueryError("Invalid argument: 'pattern' can't be empty")
	
	valid_pattern = (pattern 
		and api.utils.sql_escape(pattern.decode(api.config.api.get('encoding', 'UTF-8'))) 
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
	Arguments: idents -> string list, offset - > int, tag -> string, pattern -> string
	'''
	
	try:
		idents = args.get('idents', [])
		offset = int(args.get('offset', ['0'])[0])
		limit = int(args.get('limit', ['0'])[0])
		tag = args.get('tag', [None])[0]
		pattern = args.get('pattern', [None])[0]
	except Exception, e:
		raise QueryError('Invalid argument: ' + str(e))
	
	if not limit:
		limit = api.config.api.get('max_connections', 15)
	
	limit = min(limit, api.config.api.get('max_connections', 15))
	
	if not idents:
		raise QueryError("Invalid argument: 'idents' list can not be empty")
	
	valid_pattern = (pattern and api.utils.sql_escape(pattern.decode(api.config.api.get('encoding', 'UTF-8'))) or None)
	if pattern:
		if not api.utils.sql_valid(valid_pattern):
			raise QueryError('Invalid argument: ' + pattern)
	
	max_intersection_idents = api.config.api.get('max_intersection_idents', 3)
	if len(idents) > max_intersection_idents:
		raise QueryError("Invalid argument: 'idents' list must include not more than " + str(max_intersection_idents) + " entries")
	
	valid_idents = [ name_from_url(api.utils.sql_escape(ident.decode(api.config.api.get('encoding', 'UTF-8')))) for ident in idents ]
	for ident in valid_idents:
		if not api.utils.sql_valid(ident.get('title', u'')) or not api.utils.sql_valid(ident.get('tag', u'')):
			raise QueryError('Invalid argument: ' + ident)
	
	database = db.database.get_frontend_db_ro()
	
	db_idents = [ get_ident(database, ident.get('title', u''), ident.get('tag', u'')) for ident in valid_idents ]
	
	if (len(db_idents) != len(valid_idents)):
		invalid_idents = ( ident.encode(api.config.api.get('encoding', 'UTF-8')) for ident in valid_idents if ident not in ( ident.title for ident in db_idents ) )
		raise QueryError('Invalid argument(s): ' + ', '.join(invalid_idents))
	
	max_score = func.max(db.sqldb.Friend.score)
	
	db_connections = database.query(db.sqldb.Friend.ident_2_id, max_score)\
		.filter(db.sqldb.Friend.ident_1_id.in_((ident.id for ident in db_idents)))\
		.group_by(db.sqldb.Friend.ident_2_id)\
		.having(func.count(db.sqldb.Friend.ident_2_id) == len(db_idents))\
		.order_by(max_score.desc())
	
	if tag:
		db_connections = db_connections\
			.filter(db.sqldb.Friend.ident_2_tag == tag)
	
	if pattern:
		max_tokens = api.config.api.get('max_connections_filter_tokens', 2)
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
			'title' : connection.ident_2_title.encode(api.config.api.get('encoding', 'UTF-8')),
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
		limit = api.config.api.get('max_urls', 15)
	
	limit = min(limit, api.config.api.get('max_urls', 15))
	
	if not idents:
		raise QueryError("Invalid argument: 'idents' list can not be empty")
	
	valid_title = (title and api.utils.sql_escape(title.decode(api.config.api.get('encoding', 'UTF-8'))) or None)
	if title:
		if not api.utils.sql_valid(valid_title):
			raise QueryError('Invalid argument: ' + title)
	
	valid_domain = (domain and api.utils.sql_escape(domain.decode(api.config.api.get('encoding', 'UTF-8'))) or None)
	if domain:
		if not api.utils.sql_valid(valid_domain):
			raise QueryError('Invalid argument: ' + domain)
	
	max_intersection_idents = api.config.api.get('max_intersection_idents', 3)
	if len(idents) > max_intersection_idents:
		raise QueryError("Invalid argument: 'idents' list must include not more than " + str(max_intersection_idents) + " entries")
	
	valid_idents = [ name_from_url(api.utils.sql_escape(ident.decode(api.config.api.get('encoding', 'UTF-8')))) for ident in idents ]
	for ident in valid_idents:
		if not api.utils.sql_valid(ident.get('title', u'')) or not api.utils.sql_valid(ident.get('tag', u'')):
			raise QueryError('Invalid argument: ' + ident)
	
	database = db.database.get_frontend_db_ro()
	
	db_idents = [ get_ident(database, ident.get('title', u''), ident.get('tag', u'')) for ident in valid_idents ]
	
	if (len(db_idents) != len(valid_idents)):
		invalid_idents = ( ident.encode(api.config.api.get('encoding', 'UTF-8')) for ident in valid_idents if ident not in ( ident.title for ident in db_idents ) )
		raise QueryError('Invalid argument(s): ' + ', '.join(invalid_idents))
	
	db_web = database.query(db.sqldb.Web.url_id)\
		.filter(db.sqldb.Web.ident_id.in_(( ident.id for ident in db_idents )))\
		.group_by(db.sqldb.Web.url_id)\
		.having(func.count(db.sqldb.Web.url_id) == len(db_idents))
	
	if title:
		max_tokens = api.config.api.get('max_title_filter_tokens', 5)
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
	Arguments: ident -> string, tag - > string, level_1_offset -> int, level_2_offset -> int, pattern -> string
	'''
	
	try:
		ident = args.get('ident', [None])[0] # FIXME: rename to 'idents' as in other interfaces
		tag = args.get('tag', [None])[0]
		offset = int(args.get('offset', ['0'])[0])
		pattern = args.get('pattern', [None])[0]
	except Exception, e:
		raise QueryError('Invalid argument: ' + str(e))
	
	if not ident:
		raise QueryError("Invalid argument: 'ident' can not be empty")
	
	valid_ident = name_from_url(api.utils.sql_escape(ident.decode(api.config.api.get('encoding', 'UTF-8'))))
	if not api.utils.sql_valid(valid_ident.get('title', u'')) or not api.utils.sql_valid(valid_ident.get('tag', u'')):
		raise QueryError('Invalid argument: ' + ident)
	
	valid_pattern = (pattern and api.utils.sql_escape(pattern.decode(api.config.api.get('encoding', 'UTF-8'))) or None)
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
	
	if tag:
		db_connections_lv1 = db_connections_lv1.filter(db.sqldb.Friend.ident_2_tag == tag)
	
	if pattern:
		max_tokens = api.config.api.get('max_connections_filter_tokens', 2)
		for token in valid_pattern.split(' ')[:max_tokens]:
			db_connections_lv1 = db_connections_lv1\
				.filter(db.sqldb.Friend.ident_2_title.op('ilike')('%' + token.strip() + '%'))
	
	db_connections_lv1 = db_connections_lv1\
		.offset(offset)\
		.limit(api.config.api.get('max_pack_layer_1_size', 15))
	
	lv1_ids = [ connection.ident_2_id for connection in db_connections_lv1 ]
	lv2_ids = []
	
	if lv1_ids:
		# level 2
		db_connections_lv2 = database.query(db.sqldb.Friend.ident_2_id, max_score)\
			.filter(db.sqldb.Friend.ident_1_id.in_(lv1_ids))\
			.filter(not_(db.sqldb.Friend.ident_2_id.in_(itertools.chain(lv1_ids, (db_ident.id, )))))\
			.group_by(db.sqldb.Friend.ident_2_id)\
			.order_by(max_score.desc())
		
		if tag:
			db_connections_lv2 = db_connections_lv2\
				.filter(db.sqldb.Friend.ident_2_tag == tag)
		
		db_connections_lv2 = db_connections_lv2\
			.limit(api.config.api.get('max_pack_layer_2_size', 30))
		
		lv2_ids = [ connection.ident_2_id for connection in db_connections_lv2 ]
	
	db_connections = database.query(db.sqldb.Ident)\
		.filter(db.sqldb.Ident.id.in_(itertools.chain(lv1_ids, lv2_ids)))
	
	return frontend((
		{
			'title' : ident.title.encode(api.config.api.get('encoding', 'UTF-8')),
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
		idents = ( main_ident, secondary_ident, )
		ref = 'http://kremlin.ru' 
		
		def setUp(self):
			database = db.database.get_frontend_db_rw()
			
			ident1 = database.query(db.sqldb.Ident)\
				.filter(db.sqldb.Ident.title == self.main_ident)\
				.first()
			if ident1 == None:
				ident1 = db.sqldb.Ident(self.main_ident, 'names')
				database.add(ident1)
				
			ident2 = database.query(db.sqldb.Ident)\
				.filter(db.sqldb.Ident.title == self.secondary_ident)\
				.first()
			if ident2 == None:
				ident2 = db.sqldb.Ident(self.secondary_ident, 'names')
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
			for chunk in connections(frontend, { 'idents' : [self.main_ident], 'offset' : ['0'] }):
				fulltext += chunk
			assert(fulltext)
#			print fulltext
			
		def testJson(self):
			self.checkResults(jsonfront.dump)
	
	class ErrorsTest(unittest.TestCase):
		
		def checkInternalError(self, interface, args, argument_name):
			
			def stub_frontend(*args):
				return ''
			
			try:
				interface(stub_frontend, args)
			except QueryError, e:
#				print e
				assert('Invalid argument' in str(e) and argument_name in str(e))
		
		def testIdents(self):
			self.checkInternalError(idents, {}, 'pattern')
			self.checkInternalError(idents, {
				'pattern' : ['']
				}, 'pattern')
			self.checkInternalError(idents, {
				'pattern' : ['x'],
				'offset' : ['x'],
				}, 'int()')
			self.checkInternalError(idents, {
				'pattern' : ['x'],
				'offset' : ['0'],
				'limit' : ['x'],
				}, 'int()')
		
		def testFuzzyIdents(self):
			self.checkInternalError(fuzzy_idents, {}, 'pattern')
			self.checkInternalError(fuzzy_idents, {
				'pattern' : ['x'],
				'offset' : ['x'],
				}, 'int()')
			self.checkInternalError(fuzzy_idents, {
				'pattern' : ['x'],
				'offset' : ['0'],
				'limit' : ['x'],
				}, 'int()')
		
		def testConnections(self):
			self.checkInternalError(connections, {}, 'idents')
			self.checkInternalError(connections, {
				'idents' : []
				}, 'idents')
			self.checkInternalError(connections, {
				'idents' : ['x'],
				'offset' : ['x'],
				}, 'int()')
			self.checkInternalError(connections, {
				'idents' : ['x'],
				'offset' : ['0'],
				'limit' : ['x'],
				}, 'int()')
			self.checkInternalError(connections, {
				'idents' : ['x'] * (api.config.api.get('max_intersection_idents', 3) + 1),
				'offset' : ['0'],
				'limit' : ['0'],
				}, 'idents')
		
		def testUrls(self):
			self.checkInternalError(urls, {}, 'idents')
			self.checkInternalError(urls, {
				'idents' : []
				}, 'idents')
			self.checkInternalError(urls, {
				'idents' : ['x'],
				'offset' : ['x'],
				}, 'int()')
			self.checkInternalError(urls, {
				'idents' : ['x'],
				'offset' : ['0'],
				'limit' : ['x'],
				}, 'int()')
			self.checkInternalError(urls, {
				'idents' : ['x'] * (api.config.api.get('max_intersection_idents', 3) + 1),
				'offset' : ['0'],
				'limit' : ['0'],
				}, 'idents')
		
		def testPack(self):
			self.checkInternalError(pack, {}, 'ident')
			self.checkInternalError(pack, {
				'ident' : []
				}, 'ident')
			self.checkInternalError(fuzzy_idents, {
				'ident' : ['x'],
				'offset' : ['x'],
				}, 'int()')
	
	#TODO: test 'limit' handling
	#TODO: test aliases 

	unittest.main()
