#-*- coding: UTF-8

import api.config
import cgi


class LittleApplicationError(Exception):
	pass


import web.config


def init_memcached():
	"""Try to make use of memcached, fallback to default app if failed"""
	
	try:
		import memcache
		
		def memcached_application(environ, start_response):
			memcached_host = '%s:%d' % (
				web.config.memcached.get('host', '127.0.0.1'), 
				web.config.memcached.get('port', 11211))
			mc = memcache.Client([ memcached_host ], debug = 0)
			
			return application(environ, start_response, mc)
			
		return memcached_application
	except ImportError: 
		return application


def memcached_hack(string):
	"""memcached_pass double-encodes $args, this mimics its behavior"""
	return string.replace('%', '%25')


def parse_query(query):
	"""Extract arguments from query"""
	
	# cgi.parse_qs() instead of urlparse.parse_qs() because of python 2.5
	args = cgi.parse_qs(query)
	
	frontend = args.get('frontend', '')
	if not frontend:
		raise LittleApplicationError('Frontend not found')
	frontend = frontend[0]
	
	frontends = web.config.application.get('frontends', {})
	frontend, content_type = frontends.get(frontend, '')
	
	if not frontend or not content_type:
		raise LittleApplicationError('Frontend not found: ' + frontend)
	
	interface = args.get('interface', '')
	if not interface:
		raise LittleApplicationError('Interface not found')
	interface = interface[0]
	
	interfaces = web.config.application.get('handlers', {})
	handler = interfaces.get(interface, None)
	if not handler:
		raise LittleApplicationError('Interface not found: ' + interface)
	
	return (frontend, content_type, handler, args)


def application(environ, start_response, memcache_client = None):
	"""Application entry point"""
	
	try:
		query = environ.get('QUERY_STRING', None)
		if not query:
			raise LittleApplicationError('No request')
		
		error_message = None
		try:
			frontend, content_type, handler, args = parse_query(query)
#			print frontend, content_type, handler, args 
			result = handler(frontend, args)
			response = ''.join(result)
		
			if memcache_client:
				try:
					memcache_client.set('api:%s' % memcached_hack(query), response, 60 * 60)
				except Exception, e:
					# any exception, really
#					print e
					pass
			
		except web.application.LittleApplicationError, e:
			error_message = str(e) 
		except Exception, e:
#			print e.__class__, str(e)
			error_message = 'Internal error'
			
		if error_message:
			raise Exception(error_message)
		
		status = '200 OK'
		headers = [
			( 'Content-type', '%s; charset=%s' % (content_type, api.config.api.get('encoding', 'UTF-8')) ), 
			( 'Access-Control-Allow-Origin', '*' ), 
		]
		
		start_response(status, headers)
		
		yield response
	except Exception, e: 
		status = '500 Not OK'
		headers = [
			( 'Content-type', 'text/plain; charset=%s' % (api.config.api.get('encoding', 'UTF-8')) ), 
		]
		start_response(status, headers)
		yield str(e)


if __name__ == '__main__':
	import unittest

	unittest.main()
