#-*- coding: UTF-8

import api.jsonfront
import api.query

application = {
	'handlers' : { 
		'idents' : (api.query.idents), 
		'fuzzyidents' : (api.query.fuzzy_idents), 
		'connections' : (api.query.connections), 
		'urls' : (api.query.urls),
		'pack' : (api.query.pack),
		'stats' : (api.query.stats),  
	}, 
	'frontends' : {
		'json' : (api.jsonfront.dump, 'application/json'), 
	}, 
}

memcached = {
	'host' : '127.0.0.1',
	'port' : 11211,
}
