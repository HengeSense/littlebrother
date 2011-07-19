#-*- coding: UTF-8

import config
import sqldb

frontend_db_rw = None
frontend_db_ro = None
master_db_rw = None
master_db_ro = None


def get_frontend_db_rw():
	"""Connect to frontend DB in rw mode"""
	global frontend_db_rw
	
	if not frontend_db_rw:
		frontend_db_rw = sqldb.SqlDB(config.database.get('frontend_url', ''), autocommit = False)
		frontend_db_rw.create_all()
	return frontend_db_rw


def get_frontend_db_ro():
	"""Connect to frontend DB in ro mode"""
	global frontend_db_ro
	
	if not frontend_db_ro:
		frontend_db_ro = sqldb.SqlDB(config.database.get('frontend_url', ''), autocommit = True)
	return frontend_db_ro


def get_master_db_rw():
	"""Connect to master DB in rw mode"""
	global master_db_rw
	
	if not master_db_rw:
		master_db_rw = sqldb.SqlDB(config.database.get('master_url', ''), autocommit = False)
		master_db_rw.create_all()
	return master_db_rw


def get_master_db_ro():
	"""Connect to master DB in ro mode"""
	global master_db_ro
	
	if not master_db_ro:
		master_db_ro = sqldb.SqlDB(config.database.get('master_url', ''), autocommit = True)
	return master_db_ro


if __name__ == '__main__':
	import unittest

	unittest.main()
