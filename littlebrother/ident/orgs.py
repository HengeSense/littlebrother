#-*- coding: UTF-8

import re

companies = re.compile(ur'''\b('''
	ur'''ООО|ЗАО|ОАО|РАО'''                         # ООО|ЗАО|ОАО...
	ur'''|компания|компании|компанию|компанией'''   # компани(-я,-и,-ю,-ей)
	ur'''|агентство|агетства|агентством'''          # etc
	ur'''|группа|группы|группу|группой'''
	ur''')\s+["«]'''                                   
	ur'''([^\s].+?[^\s])'''                         # «ВЕКТОР-4+»
	ur'''["»]''',           
	re.UNICODE | re.VERBOSE | re.IGNORECASE)

# TODO: foreign companies (Ltd, etc)


def identities(plain_text):
	return [ 
		re.sub(ur'["«»]', '', ident.strip().upper()) 
		for (_, ident) in companies.findall(plain_text) ]

if __name__ == '__main__':
	import unittest
	
	class OrgsTest(unittest.TestCase):
		
		def testIt(self):
			cases = [
				(u'Гидрогенерирующая компания «РусГидро», крупнейшая в России', [ u'РУСГИДРО' ]),
				(u'стратегическая ошибка менеджмента РАО "ЕЭС России" и лично председателя', [ u'ЕЭС РОССИИ' ]),
				(u'РАО "ЕЭС России" с компанией «РусГидро»', [ u'ЕЭС РОССИИ', u'РУСГИДРО' ]),
				(u'ОАО "Пивоваренная компания "Балтика"', [ u'ПИВОВАРЕННАЯ КОМПАНИЯ БАЛТИКА' ] ), 
			]
			for case, idents in cases:
				gathered = identities(case)
				assert(len(gathered) == len(idents))
#				for ident in gathered:
#					print ident
				for ident in idents:
					assert(ident in gathered)

	unittest.main()
