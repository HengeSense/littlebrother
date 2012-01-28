#-*- coding: UTF-8

from sqlalchemy import Column, Integer, String, Float, ForeignKey, \
	UniqueConstraint, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import limits

Base = declarative_base()


class Ident(Base):
	__tablename__ = 'idents'
	__table_args__ = (
		UniqueConstraint('title', 'tag'),
		{},
	)

	id = Column(Integer, primary_key = True)
	title = Column(String(limits.max_ident_title_len), nullable = False)
	tag = Column(String(limits.max_ident_tag_len), nullable = False)
	alias = Column(Integer, ForeignKey(id, ondelete = 'cascade', onupdate = 'cascade'))
	metaphone = Column(String(limits.max_ident_metaphone_len))
	freq_1 = Column(Integer, nullable = False, default = 0)
	freq_2 = Column(Integer, nullable = False, default = 0)
	freq_3 = Column(Integer, nullable = False, default = 0)
	freq_4 = Column(Integer, nullable = False, default = 0)
	freq_5 = Column(Integer, nullable = False, default = 0)
	freq_6 = Column(Integer, nullable = False, default = 0)
	freq_7 = Column(Integer, nullable = False, default = 0)
	freq_8 = Column(Integer, nullable = False, default = 0)
	freq_9 = Column(Integer, nullable = False, default = 0)
	freq_10 = Column(Integer, nullable = False, default = 0)
	score = Column(Float, nullable = False, default = 0)

	def __init__(self, title, tag, alias = None, metaphone = None):
		self.title = title
		self.tag = tag
		self.alias = alias
		self.metaphone = metaphone
		self.freq_1 = 0
		self.freq_2 = 0
		self.freq_3 = 0
		self.freq_4 = 0
		self.freq_5 = 0
		self.freq_6 = 0
		self.freq_7 = 0
		self.freq_8 = 0
		self.freq_9 = 0
		self.freq_10 = 0
		self.score = 0


class Url(Base):
	__tablename__ = 'urls'

	id = Column(Integer, primary_key = True)
	ref = Column(String(limits.max_ref_len), nullable = False, unique = True)
	title = Column(String(limits.max_ref_title_len))

	def __init__(self, ref, title):
		self.ref = ref
		self.title = title


class Node(Base):
	__tablename__ = 'network'
	__table_args__ = (
		UniqueConstraint('ident_1_id', 'ident_2_id', 'url_id'),
		{},
	)

	id = Column(Integer, primary_key = True)
	ident_1_id = Column(Integer, ForeignKey(Ident.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	ident_2_id = Column(Integer, ForeignKey(Ident.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	url_id = Column(Integer, ForeignKey(Url.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	distance = Column(Integer, nullable = False)

	def __init__(self, ident_1, ident_2, url, distance):
		self.ident_1_id = ident_1.id
		self.ident_2_id = ident_2.id
		self.url_id = url.id
		self.distance = distance


class Link(Base):
	__tablename__ = 'links'
	__table_args__ = (
		UniqueConstraint('ident_1_id', 'ident_2_id'),
		{},
	)

	id = Column(Integer, primary_key = True)
	ident_1_id = Column(Integer, ForeignKey(Ident.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	ident_2_id = Column(Integer, ForeignKey(Ident.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	freq_1 = Column(Integer, nullable = False, default = 0)
	freq_2 = Column(Integer, nullable = False, default = 0)
	freq_3 = Column(Integer, nullable = False, default = 0)
	freq_4 = Column(Integer, nullable = False, default = 0)
	freq_5 = Column(Integer, nullable = False, default = 0)
	freq_6 = Column(Integer, nullable = False, default = 0)
	freq_7 = Column(Integer, nullable = False, default = 0)
	freq_8 = Column(Integer, nullable = False, default = 0)
	freq_9 = Column(Integer, nullable = False, default = 0)
	freq_10 = Column(Integer, nullable = False, default = 0)
	samples_number = Column(Integer, nullable = False, default = 0)
	average = Column(Float, nullable = False, default = 0)
	median = Column(Float, nullable = False, default = 0)
	score = Column(Float, nullable = False, default = 0)

	def __init__(self, ident_1, ident_2):
		self.ident_1_id = ident_1.id
		self.ident_2_id = ident_2.id
		self.samples_number = 0
		self.freq_1 = 0
		self.freq_2 = 0
		self.freq_3 = 0
		self.freq_4 = 0
		self.freq_5 = 0
		self.freq_6 = 0
		self.freq_7 = 0
		self.freq_8 = 0
		self.freq_9 = 0
		self.freq_10 = 0
		self.average = 0
		self.median = 0
		self.score = 0


class Presence(Base):
	__tablename__ = 'presence'
	__table_args__ = (
		UniqueConstraint('ident_id', 'url_id'),
		{},
	)

	id = Column(Integer, primary_key = True)
	ident_id = Column(Integer, ForeignKey(Ident.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	url_id = Column(Integer, ForeignKey(Url.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)

	def __init__(self, ident, url):
		self.ident_id = ident.id
		self.url_id = url.id


class Friend(Base):
	__tablename__ = 'friends'
	__table_args__ = (
		UniqueConstraint('ident_1_id', 'ident_2_id'),
		{},
	)

	id = Column(Integer, primary_key = True)
	ident_1_id = Column(Integer, ForeignKey(Ident.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	ident_2_id = Column(Integer, ForeignKey(Ident.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	ident_1_tag = Column(String(limits.max_ident_tag_len), nullable = False)
	ident_2_tag = Column(String(limits.max_ident_tag_len), nullable = False)
	ident_1_title = Column(String(limits.max_ident_title_len), nullable = False)
	ident_2_title = Column(String(limits.max_ident_title_len), nullable = False)
	ident_1_score = Column(Float, nullable = False, default = 0)
	ident_2_score = Column(Float, nullable = False, default = 0)
	average = Column(Float, nullable = False, default = 0)
	median = Column(Float, nullable = False, default = 0)
	score = Column(Float, nullable = False, default = 0)

	def __init__(self, ident_1, ident_2):
		self.ident_1_id = ident_1.id
		self.ident_1_tag = ident_1.tag
		self.ident_1_title = ident_1.title
		self.ident_1_score = ident_1.score
		self.ident_2_id = ident_2.id
		self.ident_2_tag = ident_2.tag
		self.ident_2_title = ident_2.title
		self.ident_2_score = ident_2.score
		self.average = 0
		self.median = 0
		self.score = 0


class Web(Base):
	__tablename__ = 'web'
	__table_args__ = (
		UniqueConstraint('ident_id', 'url_id'),
		{},
	)

	id = Column(Integer, primary_key = True)
	ident_id = Column(Integer, ForeignKey(Ident.id, ondelete = 'cascade', onupdate = 'cascade'), nullable = False)
	ident_title = Column(String(limits.max_ident_title_len), nullable = False)
	ident_tag = Column(String(limits.max_ident_tag_len), nullable = False)
	url_id = Column(Integer, nullable = False)
	url_ref = Column(String(limits.max_ref_len), nullable = False)
	url_title = Column(String(limits.max_ref_title_len))

	def __init__(self, ident, url):
		self.ident_id = ident.id
		self.ident_title = ident.title
		self.ident_tag = ident.tag
		self.url_id = url.id
		self.url_ref = url.ref
		self.url_title = url.title


class Stat(Base):
	__tablename__ = 'stats'

	key = Column(String, primary_key = True)
	value = Column(String, nullable = False)

	def __init__(self, key, value):
		self.key = key
		self.value = value


Session = sessionmaker()


class SqlDB(object):

	def __init__(self, url, autocommit):
		'''Connect to DB'''

		super(SqlDB, self).__init__()

		self.engine = create_engine(url, convert_unicode = True, echo = False)

		Session.configure(bind = self.engine, autocommit = autocommit)
		self.session = Session()

	def create_all(self):
		'''Create tables if needed'''
		Base.metadata.create_all(bind = self.engine)

	def query(self, *tables):
		'''Mapping to session's query()'''
		return self.session.query(*tables)

	def add(self, items):
		'''Mapping to session's add()'''

		if hasattr(items, '__iter__'):
			self.session.add_all(items)
		else:
			self.session.add(items)

	def delete(self, items):
		'''Mapping to session's delete()'''

		if hasattr(items, '__iter__'):
			for item in items:
				self.session.delete(item)
		else:
			self.session.delete(items)

	def commit(self):
		'''Mapping to session's commit()'''
		self.session.commit()

	def rollback(self):
		'''Mapping to session's rollback()'''
		self.session.rollback()


if __name__ == '__main__':
	import unittest

	class SqlDBTest(unittest.TestCase):
		db_url = 'postgresql://friend:friend@localhost/master'
		ident1 = u'ИВАН ПЕТРОВИЧ'
		ident2 = u'ПЕТР ИВАНЫЧ'
		tag = u'names'
		ref = u'http://localhost'
		ref_title = u'Жопа - восход, закат.'

		def setUp(self):
			self.db = SqlDB(self.db_url, autocommit = False)
			self.db.create_all()

			name = self.db.query(Ident).filter(Ident.title == self.ident1).first()
			if name != None:
				self.db.delete(name)

			name = self.db.query(Ident).filter(Ident.title == self.ident2).first()
			if name != None:
				self.db.delete(name)

			url = self.db.query(Url).filter(Url.ref == self.ref).first()
			if url != None:
				self.db.delete(url)

			self.db.commit()

			self.db = SqlDB(self.db_url, autocommit = True)

		def testIdents(self):
			name = Ident(self.ident1, self.tag)
			self.db.add(name)

			ident = self.db.query(Ident).filter(Ident.title == name.title).first()
			assert(ident != None and ident.id == name.id and ident.title == name.title)

			self.db.delete(ident)
			assert(self.db.query(Ident).filter(Ident.title == name.title).first() == None)

		def testUrls(self):
			ref = Url(self.ref, self.ref_title)
			self.db.add(ref)

			url = self.db.query(Url).filter(Url.ref == ref.ref).first()
			assert(url != None and url.id == ref.id and url.ref == ref.ref)

			self.db.delete(url)
			assert(self.db.query(Url).filter(Url.ref == ref.ref).first() == None)

		def testNodes(self):
			ident1 = Ident(self.ident1, self.tag)
			ident2 = Ident(self.ident2, self.tag)
			url = Url(self.ref, self.ref_title)

			self.db.add([ ident1, ident2 ])
			self.db.add(url)

			assert(self.db.query(Node)\
				.filter(Node.ident_1_id == ident1.id)\
				.filter(Node.ident_2_id == ident2.id)\
				.filter(Node.url_id == url.id)\
				.first() == None)
			self.db.add(Node(ident1, ident2, url, 0))

			node = self.db.query(Node)\
				.filter(Node.ident_1_id == ident1.id)\
				.filter(Node.ident_2_id == ident2.id)\
				.filter(Node.url_id == url.id)\
				.first()
			assert(node != None and node.ident_1_id == ident1.id and node.ident_2_id == ident2.id and node.url_id == url.id)

			self.db.delete(node)
			assert(self.db.query(Node)\
				.filter(Node.ident_1_id == ident1.id)\
				.filter(Node.ident_2_id == ident2.id)\
				.filter(Node.url_id == url.id)\
				.first() == None)

		def testLinks(self):
			ident1 = Ident(self.ident1, self.tag)
			ident2 = Ident(self.ident2, self.tag)

			self.db.add([ ident1, ident2 ])

			assert(self.db.query(Link)\
				.filter(Link.ident_1_id == ident1.id)\
				.filter(Link.ident_2_id == ident2.id)\
				.first() == None)
			self.db.add(Link(ident1, ident2))

			link = self.db.query(Link)\
				.filter(Link.ident_1_id == ident1.id)\
				.filter(Link.ident_2_id == ident2.id)\
				.first()
			assert(link != None and link.ident_1_id == ident1.id and link.ident_2_id == ident2.id)

			self.db.delete(link)
			assert(self.db.query(Link)\
				.filter(Link.ident_1_id == ident1.id)\
				.filter(Link.ident_2_id == ident2.id)\
				.first() == None)

		def testPresence(self):
			ident = Ident(self.ident1, self.tag)
			url = Url(self.ref, self.ref_title)

			self.db.add(ident)
			self.db.add(url)

			assert(self.db.query(Presence)\
				.filter(Presence.ident_id == ident.id)\
				.filter(Presence.url_id == url.id)\
				.first() == None)
			self.db.add(Presence(ident, url))

			presence = self.db.query(Presence)\
				.filter(Presence.ident_id == ident.id)\
				.filter(Presence.url_id == url.id)\
				.first()
			assert(presence != None and presence.ident_id == ident.id and presence.url_id == url.id)

			self.db.delete(presence)
			assert(self.db.query(Presence)\
				.filter(Presence.ident_id == ident.id)\
				.filter(Presence.url_id == url.id)\
				.first() == None)

		def testSets(self):
			ident1 = Ident(self.ident1, self.tag)
			ident2 = Ident(self.ident2, self.tag)

			self.db.add([ ident1, ident2 ])
			assert(self.db.query(Ident).filter(Ident.title == self.ident1).first() != None)
			assert(self.db.query(Ident).filter(Ident.title == self.ident2).first() != None)

			self.db.delete([ ident1, ident2 ])
			assert(self.db.query(Ident).filter(Ident.title == self.ident1).first() == None)
			assert(self.db.query(Ident).filter(Ident.title == self.ident2).first() == None)

	unittest.main()
