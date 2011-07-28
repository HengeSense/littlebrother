#-*- coding: UTF-8

import ident.names
import ident.orgs
import ident.geo


gather = {
	'providers' : (
		(ident.names.identities, 'names'),
		(ident.orgs.identities, 'orgs'),
		(ident.geo.cities, 'cities'),
		(ident.geo.regions, 'regions'),
	)
}
