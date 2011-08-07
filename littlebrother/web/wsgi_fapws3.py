#!/usr/bin/python

import fapws._evwsgi as evwsgi
import fapws.base
import sys
import web.application


def start(host, port):
	"""Fapws3 WSGI application"""
	
	evwsgi.start(host or '127.0.0.1', port or '8000')
	evwsgi.set_base_module(fapws.base)
	
	evwsgi.wsgi_cb(("/api", web.application.init_memcached()))
	
	evwsgi.set_debug(0)
	evwsgi.run()


def usage(cmd):
	print 'usage:', cmd, ' [HOST] [PORT]'


if __name__ == "__main__":
	if len(sys.argv) < 3:
		usage(sys.argv[0])
		sys.exit(1)
	
	start(sys.argv[1], sys.argv[2])
