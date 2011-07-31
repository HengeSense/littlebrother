#-*- coding: UTF-8

from ident import metaphone_ru
import StringIO
import crawling.config
import db.database
import db.limits
import db.sqldb
import html.lxmlp
import rank.average
import rank.distance
import rank.median

distance_threshold = 10 # links farther than this threshold will be ignored


class DBLimitsException(Exception):
	pass


def add_record(database, (title1, tag1), (title2, tag2), ref, ref_title, distance):
	'''Add record to DB linking two identities'''
	
	def get_ident(title, tag):
		ident = database.query(db.sqldb.Ident)\
			.filter(db.sqldb.Ident.title == title)\
			.filter(db.sqldb.Ident.tag == tag)\
			.first()
		
		if ident == None:
			ident = db.sqldb.Ident(title, tag)
			
			metaphone = metaphone_ru.metaphone(' ' in title and title.split(' ')[0] or title)
			if len(metaphone) <= db.limits.max_ident_metaphone_len:
				ident.metaphone = metaphone
			
			database.add(ident)
		
		return ident
	
	def get_node(ident1, ident2, url, distance):
		node = database.query(db.sqldb.Node)\
			.filter(db.sqldb.Node.ident_1_id == ident1.id)\
			.filter(db.sqldb.Node.ident_2_id == ident2.id)\
			.filter(db.sqldb.Node.url_id == url.id)\
			.first()
		
		added = (node == None)
		
		if node == None:
			node = db.sqldb.Node(ident1, ident2, url, distance)
			database.add(node)
		
		return (added, node)
	
	def get_link(ident1, ident2, ranked):
		link = database.query(db.sqldb.Link)\
			.filter(db.sqldb.Link.ident_1_id == ident1.id)\
			.filter(db.sqldb.Link.ident_2_id == ident2.id)\
			.first()
		
		if link == None:
			link = db.sqldb.Link(ident1, ident2)
			database.add(link)
		
		return link
	
	def get_url(ref):
		url = database.query(db.sqldb.Url)\
			.filter(db.sqldb.Url.ref == ref)\
			.first()
		
		if url == None:
			url = db.sqldb.Url(ref, title)
			database.add(url)
		
		return url
	
	def get_presence(ident, url):
		presence = database.query(db.sqldb.Presence)\
			.filter(db.sqldb.Presence.ident_id == ident.id)\
			.filter(db.sqldb.Presence.url_id == url.id)\
			.first()
		
		if presence == None:
			presence = db.sqldb.Presence(ident, url)
			database.add(presence)
		
		return presence
	
	def increase_freq(obj, number, inc):
		freq = getattr(obj, 'freq_' + str(int(number)))
		freq = int(freq) + inc
		
		if freq < 0:
			freq = 0
		
		setattr(obj, 'freq_' + str(number), freq)
	
	def get_freqs(obj):
		return [ (i, int(getattr(obj, 'freq_' + str(i))))
			for i in xrange(1, 11) ]
	
	def update_ident_score(ident):
		ident.score = (ident.freq_1 * 0.1 + 
			ident.freq_2 * 0.2 + 
			ident.freq_3 * 0.3 + 
			ident.freq_4 * 0.4 + 
			ident.freq_5 * 0.5 + 
			ident.freq_6 * 0.6 + 
			ident.freq_7 * 0.7 + 
			ident.freq_8 * 0.8 + 
			ident.freq_9 * 0.9 + 
			ident.freq_10) 
	
	
	try:
		if len(title1) > db.limits.max_ident_title_len:
			raise DBLimitsException(title1)
		
		if len(title2) > db.limits.max_ident_title_len:
			raise DBLimitsException(title2)
		
		if len(tag1) > db.limits.max_ident_tag_len:
			raise DBLimitsException(tag1)
		
		if len(tag2) > db.limits.max_ident_tag_len:
			raise DBLimitsException(tag2)
		
		if len(ref) > db.limits.max_ref_len:
			raise DBLimitsException(ref)
		
		if ref_title and len(ref_title) > db.limits.max_ref_title_len:
			ref_title = ref_title[:db.limits.max_ref_title_len - 3] + u'...'
		
		# adding found identities
		#
		ident1 = get_ident(title1, tag1)
		ident1.tag = tag1
		
		ident2 = get_ident(title2, tag2)
		ident2.tag = tag2
		
		title = ref_title
		if title and len(title) > db.limits.max_ref_title_len:
			title = title[:db.limits.max_ref_title_len - 3] + '...'
		
		# adding crawled URL
		#			
		url = get_url(ref)
		url.title = title
		
		# adding nodes
		#
		node_added, node = get_node(ident1, ident2, url, distance)
		backnode_added, backnode = get_node(ident2, ident1, url, distance)
		
		# while Node stores distance, Link stores rank
		# 
		ranked = rank.distance.rank(distance)
		
		# weights update
		#
		link = get_link(ident1, ident2, ranked)
		if not node_added:
			freq = rank.distance.rank(node.distance)
			increase_freq(link, freq, -1)
			link.samples_number -= 1
			increase_freq(ident1, freq, -1)
			increase_freq(ident2, freq, -1)
		
		increase_freq(link, ranked, 1)
		link.samples_number += 1
		link.average = rank.average.average(get_freqs(link))
		link.median = rank.median.median(get_freqs(link))
		link.score = link.median * link.samples_number
		
		increase_freq(ident1, ranked, 1)
		increase_freq(ident2, ranked, 1)
		
		update_ident_score(ident1)
		update_ident_score(ident2)
		
		backlink = get_link(ident2, ident1, ranked)
		if not backnode_added:
			increase_freq(backlink, rank.distance.rank(node.distance), -1)
			backlink.samples_number -= 1
		
		increase_freq(backlink, ranked, 1)
		backlink.samples_number += 1
		backlink.average = rank.average.average(get_freqs(backlink))
		backlink.median = rank.median.median(get_freqs(backlink))
		backlink.score = backlink.median * backlink.samples_number
		
		# distance update postponed since it's might be excluded from Link's rank
		# 
		node.distance = distance
		backnode.distance = distance
		
		get_presence(ident1, url)
		get_presence(ident2, url)
		
		database.commit()
		
	except:
		database.rollback()
		raise


def collect(text):
	'''Collect records from text'''
	
	providers = crawling.config.gather.get('providers', ())
	
	title, identities = html.lxmlp.parse_file(StringIO.StringIO(text), providers)
	
	if title:
		title = title.strip(u' \t\n\r')
	
	measured = {}
	for index, (identity, xpath, tag) in enumerate(identities):
		for other, other_xpath, other_tag in identities[index + 1:]:
			if identity == other:
				continue
			
			distance = rank.distance.xpath_distance(xpath, other_xpath)
			if distance <= distance_threshold:
				
				measured_distance = measured.get((identity, other), None)
				reverse_measured_distance = measured.get((other, identity), None)
				
				# shorter distance - better
				if reverse_measured_distance == None and (measured_distance == None or measured_distance > distance):
					measured[(identity, tag, other, other_tag)] = distance
				elif reverse_measured_distance != None and reverse_measured_distance > distance:
					measured[(other, other_tag, identity, tag)] = distance
	
	return (title, measured)


def gather(url, text):
	'''Find all identities in text and add them to DB'''
	
	title, gathered = collect(text)
	
	database = db.database.get_master_db_rw()
	for (identity, tag, other, other_tag), distance in gathered.iteritems():
		try:
			add_record(database, 
				(identity, tag), 
				(other, other_tag), 
				url, 
				title, 
				distance)
		except DBLimitsException:
			# can't add this record because of database limits
			# well, shit happens, proceed to next record
			# FIXME: log this or something 
			pass


if __name__ == '__main__':
	import unittest
	
	class GatherTest(unittest.TestCase):
		url = u'http://example.com'
		filename = u'samples/test.html'
		
		def setUp(self):
			database = db.database.get_master_db_rw()
			
			url = database.query(db.sqldb.Url)\
				.filter(db.sqldb.Url.ref == self.url)\
				.first()
			
			if url:
				database.delete(url)
				database.commit()
				
			database.rollback()
		
		def testLimits(self):
			long_title = 'x' * (db.limits.max_ident_title_len + 1)
			long_tag = 'x' * (db.limits.max_ident_tag_len + 1)
			long_ref = 'x' * (db.limits.max_ref_len + 1)
			long_ref_title = 'x' * (db.limits.max_ref_title_len + 1)
			ok_title = 'x' * (db.limits.max_ident_title_len)
			ok_tag = 'x' * (db.limits.max_ident_tag_len)
			ok_ref = 'x' * (db.limits.max_ref_len)
			ok_ref_title = 'x' * (db.limits.max_ref_title_len)
			
			database = db.database.get_master_db_rw()
			assert(database != None)
			
			idents = database.query(db.sqldb.Ident)\
				.filter(db.sqldb.Ident.title == ok_title)\
				.all()
			database.delete(idents)
			
			urls = database.query(db.sqldb.Url)\
				.filter(db.sqldb.Url.ref == ok_ref)\
				.all()
			database.delete(urls)
			
			database.commit()
			
			try:
				add_record(database, (ok_title, ok_tag), (ok_title, ok_tag), ok_ref, ok_ref_title, 0)
			except DBLimitsException:
				assert("DBLimitsException shouln't be raised here")
						
			try:
				add_record(database, (long_title, ok_tag), (ok_title, ok_tag), ok_ref, ok_ref_title, 0)
				assert(not "thou shall not pass")
			except DBLimitsException:
				pass
			
			try:
				add_record(database, (ok_title, long_tag), (ok_title, ok_tag), ok_ref, ok_ref_title, 0)
				assert(not "thou shall not pass")
			except DBLimitsException:
				pass
			
			try:
				add_record(database, (ok_title, ok_tag), (long_title, ok_tag), ok_ref, ok_ref_title, 0)
				assert(not "thou shall not pass")
			except DBLimitsException:
				pass
			
			try:
				add_record(database, (ok_title, ok_tag), (ok_title, long_tag), ok_ref, ok_ref_title, 0)
				assert(not "thou shall not pass")
			except DBLimitsException:
				pass
			
			try:
				add_record(database, (ok_title, ok_tag), (ok_title, ok_tag), long_ref, ok_ref_title, 0)
				assert(not "thou shall not pass")
			except DBLimitsException:
				pass
			
			try:
				add_record(database, (ok_title, ok_tag), (ok_title, ok_tag), ok_ref, long_ref_title, 0)
			except DBLimitsException: 
				assert("DBLimitsException shouln't be raised here")
		
		def testAddRecord(self):
			name1 = u'ПЕТРОВИЧ ИВАН'
			name2 = u'ИВАНЫЧ ПЕТР'
			tag = 'names'
			distance = 4
			
			database = db.database.get_master_db_rw()
			assert(database != None)
			
			ident1 = database.query(db.sqldb.Ident).filter(db.sqldb.Ident.title == name1).first()
			if ident1:
				database.delete(ident1)
			
			ident2 = database.query(db.sqldb.Ident).filter(db.sqldb.Ident.title == name2).first()
			if ident2:
				database.delete(ident2)
			
			database.commit()
			
			add_record(database, (name1, tag), (name2, tag), self.url, "", distance)
			database.commit()
			
			ident1 = database.query(db.sqldb.Ident).filter(db.sqldb.Ident.title == name1).first()
			ident2 = database.query(db.sqldb.Ident).filter(db.sqldb.Ident.title == name2).first()
			assert(ident1 != None and ident1.title == name1)
			assert(ident2 != None and ident2.title == name2)
			
			assert(ident1.score > 0)
			assert(ident2.score > 0)
			assert(ident1.score == ident2.score)
			
			url = database.query(db.sqldb.Url).filter(db.sqldb.Url.ref == self.url).first()
			assert(url != None and url.ref == self.url)
				
			node = database.query(db.sqldb.Node)\
				.filter(db.sqldb.Node.ident_1_id == ident1.id)\
				.filter(db.sqldb.Node.ident_2_id == ident2.id)\
				.filter(db.sqldb.Node.url_id == url.id)\
				.first()
			assert(node != None)
			assert(node.distance == distance)
			
			node = database.query(db.sqldb.Node)\
				.filter(db.sqldb.Node.ident_1_id == ident2.id)\
				.filter(db.sqldb.Node.ident_2_id == ident1.id)\
				.filter(db.sqldb.Node.url_id == url.id)\
				.first()
			assert(node != None)
			assert(node.distance == distance)
			
			link = database.query(db.sqldb.Link)\
				.filter(db.sqldb.Link.ident_1_id == ident1.id)\
				.filter(db.sqldb.Link.ident_2_id == ident2.id)\
				.first()
			assert(link != None)
			assert(link.samples_number == 1)
			assert(link.score == link.median * link.samples_number)
				
			link = database.query(db.sqldb.Link)\
				.filter(db.sqldb.Link.ident_1_id == ident2.id)\
				.filter(db.sqldb.Link.ident_2_id == ident1.id)\
				.first()
			assert(link != None)
			assert(link.samples_number == 1)
			assert(link.score == link.median * link.samples_number)
			
			presence = database.query(db.sqldb.Presence)\
				.filter(db.sqldb.Presence.ident_id == ident1.id)\
				.filter(db.sqldb.Presence.url_id == url.id)\
				.first()
			assert(presence != None)
			
			presence = database.query(db.sqldb.Presence)\
				.filter(db.sqldb.Presence.ident_id == ident2.id)\
				.filter(db.sqldb.Presence.url_id == url.id)\
				.first()
			assert(presence != None)
			
			old_average = link.average
			old_median = link.median
			old_link_score = link.score
			old_ident1_score = ident1.score
			old_ident2_score = ident2.score
			
			# add record again to check if it's not breaking anything 
			add_record(database, (name1, tag), (name2, tag), self.url, "", distance)
			
			ident1 = database.query(db.sqldb.Ident).filter(db.sqldb.Ident.title == name1).first()
			ident2 = database.query(db.sqldb.Ident).filter(db.sqldb.Ident.title == name2).first()
			assert(ident1 != None)
			assert(ident2 != None)
			assert(ident1.score == ident2.score)
			assert(ident1.score == old_ident1_score)
			assert(ident2.score == old_ident2_score)
			
			link = database.query(db.sqldb.Link)\
				.filter(db.sqldb.Link.ident_1_id == ident1.id)\
				.filter(db.sqldb.Link.ident_2_id == ident2.id)\
				.first()	
			
			assert(link != None)
			assert(link.samples_number == 1)
			assert(link.average == old_average)
			assert(link.median == old_median)
			assert(link.score == old_link_score)
			
			link = database.query(db.sqldb.Link)\
				.filter(db.sqldb.Link.ident_1_id == ident2.id)\
				.filter(db.sqldb.Link.ident_2_id == ident1.id)\
				.first()
			assert(link != None)
			assert(link.samples_number == 1)
			assert(link.average == old_average)
			assert(link.median == old_median)
		
		def _testFromFile(self):
			title, gathered = collect(open(self.filename, 'rt').read())
			assert(title)
			assert(len(gathered) > 0)
			for ((identity, tag, other, other_tag), distance) in gathered.iteritems():
#				print identity, other
				assert(identity)
				assert(tag)
				assert(other)
				assert(other_tag)
				assert(distance <= distance_threshold)
		
		def testGathering(self):
			title, gathered = collect(open(self.filename, 'rt').read())
			assert(title)
			assert(len(gathered) > 0)
			
			gather(self.url, open(self.filename, 'rt').read())
			
			database = db.database.get_master_db_ro()
			
			for item in gathered.iteritems():
				ident, tag, other, other_tag = item[0] # item[1] is distance (unused)
				
				ident1 = database.query(db.sqldb.Ident)\
					.filter(db.sqldb.Ident.title == ident)\
					.filter(db.sqldb.Ident.tag == tag)\
					.all()
				assert(ident1 and len(ident1) == 1)
				
				ident2 = database.query(db.sqldb.Ident)\
					.filter(db.sqldb.Ident.title == other)\
					.filter(db.sqldb.Ident.tag == other_tag)\
					.all()
				assert(ident2 and len(ident2) == 1)
				
				url = database.query(db.sqldb.Url)\
					.filter(db.sqldb.Url.ref == self.url)\
					.all()
				assert(url and len(url) == 1)
				
				node = database.query(db.sqldb.Node)\
					.filter(db.sqldb.Node.ident_1_id == ident1[0].id)\
					.filter(db.sqldb.Node.ident_2_id == ident2[0].id)\
					.first()
				assert(node)
				
				node = database.query(db.sqldb.Node)\
					.filter(db.sqldb.Node.ident_1_id == ident2[0].id)\
					.filter(db.sqldb.Node.ident_2_id == ident1[0].id)\
					.first()
				assert(node)
				
				link = database.query(db.sqldb.Link)\
					.filter(db.sqldb.Link.ident_1_id == ident1[0].id)\
					.filter(db.sqldb.Link.ident_2_id == ident2[0].id)\
					.first()
				assert(link)
				
				link = database.query(db.sqldb.Link)\
					.filter(db.sqldb.Link.ident_1_id == ident2[0].id)\
					.filter(db.sqldb.Link.ident_2_id == ident1[0].id)\
					.first()
				assert(link)

	unittest.main()
