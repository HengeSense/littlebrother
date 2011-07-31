#-*- coding: UTF-8

from sqlalchemy.orm import aliased
import db.database
import db.sqldb

transaction_len = 1000
idents_job, friends_job, web_job, stats_job = range(4)
stage_1, stage_2 = range(2)


def progress(current, total):
	if total < 1:
		return 100
	
	return int(current / (total / 100.0))


def copy_idents(from_db, to_db, callback = None):
	'''Copy idents from master to frontend'''
	
	if callback:
		callback(stage_1, 0)
	
	to_db.query(db.sqldb.Ident).delete()
	
	if callback:
		callback(stage_1, 100)
		callback(stage_2, 0)
	
	total_idents = from_db.query(db.sqldb.Ident).count()
	if total_idents < 1:
		callback(stage_2, 100)
		return
	
	for i, ident in enumerate(from_db.query(db.sqldb.Ident).yield_per(transaction_len)):
		copy = db.sqldb.Ident(ident.title, ident.tag, metaphone = ident.metaphone)
		copy.id = ident.id
		copy.alias = ident.alias
		copy.score = ident.score
		
		to_db.add(copy)
		
		if i % transaction_len == 0:
			to_db.commit()
		
		if callback and i % transaction_len == 0:
			callback(stage_2, progress(i, total_idents))
	
	to_db.commit()
	
	if callback:
		callback(stage_2, 100)


def create_friends(from_db, to_db, callback = None):
	'''Fill friends'''
	
	if callback:
		callback(stage_1, 0)
	
	to_db.query(db.sqldb.Friend).delete()
	
	if callback: 
		callback(stage_1, 100)
		callback(stage_2, 0)
		
	total_links = from_db.query(db.sqldb.Link).count()
	if total_links < 1:
		callback(stage_2, 100)
		return
	
	idents_alias_1 = aliased(db.sqldb.Ident)
	idents_alias_2 = aliased(db.sqldb.Ident)
	
	query = from_db.query(db.sqldb.Link, idents_alias_1, idents_alias_2)\
		.join(( idents_alias_1, db.sqldb.Link.ident_1_id == idents_alias_1.id ))\
		.join(( idents_alias_2, db.sqldb.Link.ident_2_id == idents_alias_2.id ))\
		.yield_per(transaction_len)
	
	for i, (link, ident_1, ident_2) in enumerate(query):
		copy = db.sqldb.Friend(ident_1, ident_2)
		copy.average = link.average
		copy.median = link.median
		copy.score = link.score
		
		copy.ident_1_tag = ident_1.tag
		copy.ident_1_title = ident_1.title
		copy.ident_2_tag = ident_2.tag
		copy.ident_2_title = ident_2.title
		
		to_db.add(copy)
		
		if i % transaction_len == 0:
			to_db.commit()
		
		if callback and i % transaction_len == 0:
			callback(stage_2, progress(i, total_links))
	
	to_db.commit()
	
	if callback:
		callback(stage_2, 100)


def create_web(from_db, to_db, callback = None):
	'''Fill web'''
	
	if callback:
		callback(stage_1, 0)
	
	to_db.query(db.sqldb.Web).delete()
	
	if callback: 
		callback(stage_1, 100)
		callback(stage_2, 0)
	
	total_presence = from_db.query(db.sqldb.Presence).count()
	if total_presence < 1:
		callback(stage_2, 100)
		return
	
	idents_alias = aliased(db.sqldb.Ident)
	urls_alias = aliased(db.sqldb.Url)
	
	query = from_db.query(db.sqldb.Presence, idents_alias, urls_alias)\
		.join(( idents_alias, db.sqldb.Presence.ident_id == idents_alias.id ))\
		.join(( urls_alias, db.sqldb.Presence.url_id == urls_alias.id ))\
		.yield_per(transaction_len)
	
	for i, (_, ident, url) in enumerate(query):
		copy = db.sqldb.Web(ident, url)
		
		to_db.add(copy)
		
		if i % transaction_len == 0:
			to_db.commit()
		
		if callback and i % transaction_len == 0:
			callback(stage_2, progress(i, total_presence))
			
	to_db.commit()
	
	if callback:
		callback(stage_2, 100)


def fill_stats(to_db, callback = None):
	'''Fill stats'''
	
	if callback:
		callback(stage_1, 0)
	
	to_db.query(db.sqldb.Stat).delete()
	
	if callback: 
		callback(stage_1, 100)
		callback(stage_2, 0)
	
	total_idents = to_db.query(db.sqldb.Ident).count()
	total_names = to_db.query(db.sqldb.Ident).filter(db.sqldb.Ident.tag == 'names').count()
	total_orgs = to_db.query(db.sqldb.Ident).filter(db.sqldb.Ident.tag == 'orgs').count()
	top_ident = to_db.query(db.sqldb.Ident).order_by(db.sqldb.Ident.score.desc()).limit(1).first()
	bottom_ident = to_db.query(db.sqldb.Ident).order_by(db.sqldb.Ident.score).limit(1).first()
	top_name = to_db.query(db.sqldb.Ident).filter(db.sqldb.Ident.tag == 'names').order_by(db.sqldb.Ident.score.desc()).limit(1).first()
	bottom_name = to_db.query(db.sqldb.Ident).filter(db.sqldb.Ident.tag == 'names').order_by(db.sqldb.Ident.score).limit(1).first()
	top_org = to_db.query(db.sqldb.Ident).filter(db.sqldb.Ident.tag == 'orgs').order_by(db.sqldb.Ident.score.desc()).limit(1).first()
	bottom_org = to_db.query(db.sqldb.Ident).filter(db.sqldb.Ident.tag == 'orgs').order_by(db.sqldb.Ident.score).limit(1).first()
	total_urls = to_db.query(db.sqldb.Web.url_id).group_by(db.sqldb.Web.url_id).count()
	total_records = to_db.query(db.sqldb.Ident).count() + to_db.query(db.sqldb.Friend).count() + to_db.query(db.sqldb.Web).count()
	
	to_db.add(db.sqldb.Stat('total_idents', str(total_idents)))
	to_db.add(db.sqldb.Stat('total_names', str(total_names)))
	to_db.add(db.sqldb.Stat('total_orgs', str(total_orgs)))
	to_db.add(db.sqldb.Stat('top_ident', top_ident.title))
	to_db.add(db.sqldb.Stat('bottom_ident', bottom_ident.title))
	to_db.add(db.sqldb.Stat('top_name', top_name.title))
	to_db.add(db.sqldb.Stat('bottom_name', bottom_name.title))
	to_db.add(db.sqldb.Stat('top_org', top_org.title))
	to_db.add(db.sqldb.Stat('bottom_org', bottom_org.title))
	to_db.add(db.sqldb.Stat('total_urls', str(total_urls)))
	to_db.add(db.sqldb.Stat('total_records', str(total_records)))
	
	to_db.commit()
	
	if callback:
		callback(stage_2, 100)


def create_frontend(callback = None):
	'''Fill frontend DB with master's data'''
	
	master = db.database.get_master_db_ro()
	frontend = db.database.get_frontend_db_rw()

	# short jobs first
	copy_idents(master, 
		frontend, 
		lambda substage, progress: callback(idents_job, substage, progress))
	create_web(master, 
		frontend, 
		lambda substage, progress: callback(web_job, substage, progress))
	create_friends(master, 
		frontend, 
		lambda substage, progress: callback(friends_job, substage, progress))
	fill_stats(frontend, 
		lambda substage, progress: callback(stats_job, substage, progress))


if __name__ == '__main__':
	import sys
	
	def print_callback(stage, substage, progress):
		
		class StageError(Exception):
			pass
		
		try:
			if stage == idents_job:
				if substage == stage_1:
					sys.stdout.write('Deleting idents: %d%% done' % progress)
				elif substage == stage_2:
					sys.stdout.write('Copying idents: %d%% done' % progress)
				else:
					raise StageError('Unknown substage: %d' % substage)
			elif stage == friends_job:
				if substage == stage_1:
					sys.stdout.write('Deleting friends: %d%% done' % progress)
				elif substage == stage_2:
					sys.stdout.write('Making new friends: %d%% done' % progress)
				else:
					raise StageError('Unknown substage: %d' % substage)
			elif stage == web_job:
				if substage == stage_1:
					sys.stdout.write('Deleting web: %d%% done' % progress)
				elif substage == stage_2:
					sys.stdout.write('Creating web: %d%% done' % progress)
				else:
					raise StageError('Unknown substage: %d' % substage)
			elif stage == stats_job:
				if substage == stage_1:
					sys.stdout.write('Deleting stats: %d%% done' % progress)
				elif substage == stage_2:
					sys.stdout.write('Filling stats: %d%% done' % progress)
				else:
					raise StageError('Unknown substage: %d' % substage)
			else:
				raise StageError('Unknown stage: %d' % stage)
		except StageError, e:
			sys.stdout.write('%s: %d%% done' % (str(e), progress))
		
		if progress >= 100:
			sys.stdout.write('\n')
		else:
			sys.stdout.write('\r')
		
		sys.stdout.flush()


if __name__ == '__main__':
	create_frontend(print_callback)
