#-*- coding: UTF-8

#from ident import metaphone_ru
import StringIO
import crawling.config
import html.lxmlp
#import db.database
#import db.limits
#import db.sqldb
#import rank.average
#import rank.distance
#import rank.median

DISTANCE_THRESHOLD = 10  # links farther than this threshold will be ignored


#class DBLimitsException(Exception):
#	pass


#def add_record(database, (title1, tag1), (title2, tag2), ref, ref_title, distance):
#	'''Add record to DB linking two identities'''
#
#	def get_ident(title, tag):
#		ident = database.query(db.sqldb.Ident)\
#			.filter(db.sqldb.Ident.title == title)\
#			.filter(db.sqldb.Ident.tag == tag)\
#			.first()
#
#		if ident == None:
#			ident = db.sqldb.Ident(title, tag)
#
#			metaphone = metaphone_ru.metaphone(' ' in title and title.split(' ')[0] or title)
#			if len(metaphone) <= db.limits.max_ident_metaphone_len:
#				ident.metaphone = metaphone
#
#			database.add(ident)
#
#		return ident
#
#	def get_node(ident1, ident2, url, distance):
#		node = database.query(db.sqldb.Node)\
#			.filter(db.sqldb.Node.ident_1_id == ident1.id)\
#			.filter(db.sqldb.Node.ident_2_id == ident2.id)\
#			.filter(db.sqldb.Node.url_id == url.id)\
#			.first()
#
#		added = (node == None)
#
#		if node == None:
#			node = db.sqldb.Node(ident1, ident2, url, distance)
#			database.add(node)
#
#		return (added, node)
#
#	def get_link(ident1, ident2, ranked):
#		link = database.query(db.sqldb.Link)\
#			.filter(db.sqldb.Link.ident_1_id == ident1.id)\
#			.filter(db.sqldb.Link.ident_2_id == ident2.id)\
#			.first()
#
#		if link == None:
#			link = db.sqldb.Link(ident1, ident2)
#			database.add(link)
#
#		return link
#
#	def get_url(ref):
#		url = database.query(db.sqldb.Url)\
#			.filter(db.sqldb.Url.ref == ref)\
#			.first()
#
#		if url == None:
#			url = db.sqldb.Url(ref, title)
#			database.add(url)
#
#		return url
#
#	def get_presence(ident, url):
#		presence = database.query(db.sqldb.Presence)\
#			.filter(db.sqldb.Presence.ident_id == ident.id)\
#			.filter(db.sqldb.Presence.url_id == url.id)\
#			.first()
#
#		if presence == None:
#			presence = db.sqldb.Presence(ident, url)
#			database.add(presence)
#
#		return presence
#
#	def increase_freq(obj, number, inc):
#		freq = getattr(obj, 'freq_' + str(int(number)))
#		freq = int(freq) + inc
#
#		if freq < 0:
#			freq = 0
#
#		setattr(obj, 'freq_' + str(number), freq)
#
#	def get_freqs(obj):
#		return [ (i, int(getattr(obj, 'freq_' + str(i))))
#			for i in xrange(1, 11) ]
#
#	def update_ident_score(ident):
#		ident.score = (ident.freq_1 * 0.1 +
#			ident.freq_2 * 0.2 +
#			ident.freq_3 * 0.3 +
#			ident.freq_4 * 0.4 +
#			ident.freq_5 * 0.5 +
#			ident.freq_6 * 0.6 +
#			ident.freq_7 * 0.7 +
#			ident.freq_8 * 0.8 +
#			ident.freq_9 * 0.9 +
#			ident.freq_10)
#
#	try:
#		if len(title1) > db.limits.max_ident_title_len:
#			raise DBLimitsException(title1)
#
#		if len(title2) > db.limits.max_ident_title_len:
#			raise DBLimitsException(title2)
#
#		if len(tag1) > db.limits.max_ident_tag_len:
#			raise DBLimitsException(tag1)
#
#		if len(tag2) > db.limits.max_ident_tag_len:
#			raise DBLimitsException(tag2)
#
#		if len(ref) > db.limits.max_ref_len:
#			raise DBLimitsException(ref)
#
#		if ref_title and len(ref_title) > db.limits.max_ref_title_len:
#			ref_title = ref_title[:db.limits.max_ref_title_len - 3] + u'...'
#
#		# adding found identities
#		#
#		ident1 = get_ident(title1, tag1)
#		ident1.tag = tag1
#
#		ident2 = get_ident(title2, tag2)
#		ident2.tag = tag2
#
#		title = ref_title
#		if title and len(title) > db.limits.max_ref_title_len:
#			title = title[:db.limits.max_ref_title_len - 3] + '...'
#
#		# adding crawled URL
#		#
#		url = get_url(ref)
#		url.title = title
#
#		# adding nodes
#		#
#		node_added, node = get_node(ident1, ident2, url, distance)
#		backnode_added, backnode = get_node(ident2, ident1, url, distance)
#
#		# while Node stores distance, Link stores rank
#		#
#		ranked = rank.distance.rank(distance)
#
#		# weights update
#		#
#		link = get_link(ident1, ident2, ranked)
#		if not node_added:
#			freq = rank.distance.rank(node.distance)
#			increase_freq(link, freq, -1)
#			link.samples_number -= 1
#			increase_freq(ident1, freq, -1)
#			increase_freq(ident2, freq, -1)
#
#		increase_freq(link, ranked, 1)
#		link.samples_number += 1
#		link.average = rank.average.average(get_freqs(link))
#		link.median = rank.median.median(get_freqs(link))
#		link.score = link.median * link.samples_number
#
#		increase_freq(ident1, ranked, 1)
#		increase_freq(ident2, ranked, 1)
#
#		update_ident_score(ident1)
#		update_ident_score(ident2)
#
#		backlink = get_link(ident2, ident1, ranked)
#		if not backnode_added:
#			increase_freq(backlink, rank.distance.rank(node.distance), -1)
#			backlink.samples_number -= 1
#
#		increase_freq(backlink, ranked, 1)
#		backlink.samples_number += 1
#		backlink.average = rank.average.average(get_freqs(backlink))
#		backlink.median = rank.median.median(get_freqs(backlink))
#		backlink.score = backlink.median * backlink.samples_number
#
#		# distance update postponed since it's might be excluded from Link's rank
#		#
#		node.distance = distance
#		backnode.distance = distance
#
#		get_presence(ident1, url)
#		get_presence(ident2, url)
#
#		database.commit()
#
#	except:
#		database.rollback()
#		raise

def extract(text):
	providers = crawling.config.gather.get('providers', ())

	title, identities = html.lxmlp.parse_file(StringIO.StringIO(text), providers)
	return title, identities


#def collect(text):
#	'''Collect records from text'''
#
#	title, identities = extract(text)
#
#	if title:
#		title = title.strip(u' \t\n\r')
#
#	measured = {}
#	for index, (identity, xpath, tag) in enumerate(identities):
#		for other, other_xpath, other_tag in identities[index + 1:]:
#			if identity == other:
#				continue
#
#			distance = rank.distance.xpath_distance(xpath, other_xpath)
#			if distance <= DISTANCE_THRESHOLD:
#
#				measured_distance = measured.get((identity, other), None)
#				reverse_measured_distance = measured.get((other, identity), None)
#
#				# shorter distance - better
#				if reverse_measured_distance == None and (measured_distance == None or measured_distance > distance):
#					measured[(identity, tag, other, other_tag)] = distance
#				elif reverse_measured_distance != None and reverse_measured_distance > distance:
#					measured[(other, other_tag, identity, tag)] = distance
#
#	return (title, measured)


#def gather(url, text):
#	'''Find all identities in text and add them to DB'''
#
#	title, gathered = collect(text)
#
#	database = db.database.get_master_db_rw()
#	for (identity, tag, other, other_tag), distance in gathered.iteritems():
#		try:
#			add_record(database,
#				(identity, tag),
#				(other, other_tag),
#				url,
#				title,
#				distance)
#		except DBLimitsException:
#			# can't add this record because of database limits
#			# well, shit happens, proceed to next record
#			# FIXME: log this or something
#			pass


if __name__ == '__main__':
	import unittest

	class ExtractionTest(unittest.TestCase):
		filename = u'samples/test.html'

		def testIt(self):
			title, identities = extract(open(self.filename, 'rt').read())
			self.assertGreater(len(title), 0)
			self.assertGreater(len(identities), 0)

	unittest.main()
