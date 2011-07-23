#-*- coding: UTF-8

import ident.names
import ident.orgs


gather = {
	'providers' : ( 
		(ident.names.identities, 'names'), 
		(ident.orgs.identities, 'orgs'), 
	)
}
