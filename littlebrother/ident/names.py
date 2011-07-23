#-*- coding: UTF-8

from morphy.contrib import lastnames_ru
import config
import pymorphy
import re

name_pattern = re.compile(u'^[А-ЯЁ][а-яё]+$')
max_rate = 5
no_rate = -1

splitter = re.compile(r'([,\.!\?:;\s\n\t])', re.UNICODE)


def tokenize(string):
	'''Split string to words'''
	return [ 
		item.strip() for item in splitter.split(string) if len(item.strip()) > 0 
	]


def morph_word(string):
	'''Prepares name for morph analysis'''
	return string.upper().replace(u'Ё', u'Е')


class Morph(object):
	dicts_dir = config.dicts.get('path', 'dicts/ru/shelve45')
	dicts_type = config.dicts.get('backend', 'shelve')
	
	def __init__(self):
		super(Morph, self).__init__()
		
		self.morph = pymorphy.get_morph(self.dicts_dir, self.dicts_type)

	def is_first_name(self, word):
		'''Return true if word is considered as firstname'''
		
		info = self.morph.get_graminfo(morph_word(word))
		if len(info) < 1:
			return False
		
		for info_item in info:
			if info_item.get('class', '') == u'С':
				tags = info_item.get('info', '').split(',')
#				print ','.join(tags)
				# accept only records with 4 tags because get_name_tags expects exactly this number
				if len(tags) >= 4 \
				and u'имя' in tags and (u'мр' in tags or u'жр' in tags) \
				and u'мн' not in tags:
					return True

	def get_name_tags(self, word):
		info = self.morph.get_graminfo(morph_word(word))
		candidate = None
		for info_item in info:
			tags = info_item.get('info', '').split(',')
			
			if len(tags) < 4:
				continue
			
			gender, case = tags[0], tags[3]
			if gender not in (u'мр', u'жр',) \
			or u'мн' in tags \
			or case not in (u'им', u'рд', u'дт', u'вн', u'тв', u'пр',):
				continue
			
			return (gender, case)
						
		return (candidate or (u'мр', u'им'))

	def normal_form(self, word, gender_tag):
		'''Returns normal form of first name'''
		return self.morph.inflect_ru(morph_word(word), u'им,ед,%s' % (gender_tag))
	
	def lastname_normal_form(self, word, gender_tag):
		'''Returns normal form of last name'''
		return lastnames_ru.lastname_normal_form_ru(self.morph, morph_word(word), gender_tag)
	
	def decline_lastname(self, word, gender_tag):
		return lastnames_ru.decline_lastname_ru(morph_word(word), gender_tag)
	
	def get_graminfo(self, word):
		return self.morph.get_graminfo(morph_word(word))


def rate_last_name(morph, word, gender_tag, case):
	'''Give rating to word as for lastname. bigger is better'''
	
	info = morph.get_graminfo(morph_word(word))
	rate = 0
	for info_item in info:
		tags = info_item.get('info', '').split(',')
		if u'отч' in tags:
			return no_rate + 1 # 
		elif u'фам' in tags:
			return max_rate
		if case in tags:
			rate += 1
	
	if morph.is_first_name(word):
		rate += 1
	
	return rate


morph = Morph()


def identities(plain_text):
	
	def decide_rate(token, gender_tag, case):
		same_case = False
		
#		print 'decide on', token, 'need case', case
		info = morph.get_graminfo(morph_word(token))
		if len(info) > 0:
			for info_item in info:
				tags = info_item.get('info', '').split(',')
#				print '<<<', ','.join(tags)
				if case in tags or u'мр-жр' in tags or u'ср' in tags:
					same_case = True
					break
					
		if not same_case:
#			print 'skipping', token, 'since it is in another case'
			return (morph.lastname_normal_form(token, gender_tag), no_rate)
		
		word = morph_word(token)
		decline_rate = None
		
		# check if it's surname as lastname_normal_form_ru does
		for item in lastnames_ru.decline_lastname_ru(word, gender_tag):
			if item.get('word', '') == word:
				decline_rate = (item.get('norm', word), max_rate)
				break
		
		# ok, given gender didn't match
		# but try other gender, in case if gender mismatched
		fixed_gender_tag = (gender_tag == u'мр' and u'жр' or u'мр')
		for index, item in enumerate(lastnames_ru.decline_lastname_ru(word, fixed_gender_tag)):
			if item.get('word', '') == word:
				# yes, we've found result, but we need to return result from original gender
				decline_rate = (lastnames_ru.decline_lastname_ru(word, gender_tag)[index]['norm'], max_rate)
				break
		
		# additionally check for middle name and if it is, then reset rate
		if decline_rate:
			for item in morph.get_graminfo(word):
				if u'отч' in item['info']:
					decline_rate = None
					break 
				
		if decline_rate:
			return decline_rate
		
		normal_token = morph.lastname_normal_form(token, gender_tag)
		return (normal_token, rate_last_name(morph, token, gender_tag, case))

	ret = []

	tokens = tokenize(plain_text)
	tokens_len = len(tokens)
	
	skip = 0
	skipped = 0
	for i in xrange(tokens_len):
		if skip > 0: 
			skip -= 1
			skipped = i
			continue
		
		if not name_pattern.match(tokens[i]):
			continue
		
		# pymorphy is doing first names the best
		# so analysis starts if pymorphy detects first name in text
		if morph.is_first_name(tokens[i]):
			gender_tag, case = morph.get_name_tags(tokens[i])
			token = morph.normal_form(tokens[i], gender_tag)
			
#			print tokens[i], token, gender_tag, case
			
			# case: СКОВОРОДА ВАСИЛИЙ
			left = {}
			# ignore last names found at first word of the sentence
			# as in 'уже в ближайшие дни. Но Арсений отказался'
			# this will probably skip some valid names, but it's too ambiguous case 
			# and it introduces too much garbage
			#
			# doesn't include cases like 'уже в ближайшие дни. Но Арсений Яценюк отказался' though
			#
			# also skip left if it was already processed (i - 1 <= skipped)
			if i > 1 and tokens[i - 2] != '.': 
				if i - 1 > skipped and name_pattern.match(tokens[i - 1]):
					left = { 
						'rate' : decide_rate(tokens[i - 1], gender_tag, case), 
						'skip' : 0
					}
					
					if left['rate'][1] == no_rate:
						left = {}
			
			# case: ВАСИЛИЙ СКОВОРОДА
			right = {}
			if i < tokens_len - 1 and name_pattern.match(tokens[i + 1]):
#				if not morph.is_first_name(tokens[i + 2]):
				right = { 
					'rate' : decide_rate(tokens[i + 1], gender_tag, case), 
					'skip' : 1, 
				}
				
				if right['rate'][1] == no_rate:
					right = {}
			
			# case: ВАСИЛИЙ ПЕТРОВИЧ СКОВОРОДА
			next = {}	
			if i < tokens_len - 2 \
			and name_pattern.match(tokens[i + 1]) \
			and name_pattern.match(tokens[i + 2]) \
			and not morph.is_first_name(tokens[i + 2]):
				next = { 
					'rate' : decide_rate(tokens[i + 2], gender_tag, case), 
					'skip' : 2, 
				}
				
				if next['rate'][1] == no_rate:
					next = {}
			
#			if left and left['rate'][1] > no_rate: print 'left:', left['rate'][0], left['rate'][1]
#			if right and right['rate'][1] > no_rate: print 'right:', right['rate'][0], right['rate'][1]
#			if next and next['rate'][1] > no_rate: print 'next:', next['rate'][0], next['rate'][1]
			
			best = {}
			
			# obvious choices
			if left and not right and not next:
				best = left
			elif right and not left and not next:
				best = right
			elif next and not left and not right:
				best = next
			# case: 'БЛОК ВИТАЛИЯ КЛИЧКО'
			# case 'ПУТИН ВЛАДИМИР ВЛАДИМИРОВИЧ'
			# left might also be qualified for last name, but prefer right if it's not worse than left 
			elif not next and left and right:
				best = ((right['rate'][1] >= left['rate'][1]) and right or left)
			# case: 'ВЛАДИМИР ВЛАДИМИРОВИЧ ПУТИН'
			elif not left and right and next:
				best = ((next['rate'][1] >= right['rate'][1]) and next or right)
			
#			print 'best:', best	
			
			if best:
				ret.append(best['rate'][0] + ' ' + token)
				skip = best['skip'] 
			
	return ret

if __name__ == '__main__':
	import unittest
	
	class TokenizerTest(unittest.TestCase):
		
		def testIt(self):
			tokens = [ u'хуй', u'пизда', u'анархия' ]
			dirty_tokens = [ token + u'!' for token in tokens ]
			
			assert(tokenize(' '.join(tokens)) == tokens)
			assert(len(tokenize(' '.join(dirty_tokens))) == len(tokens) * 2)

	class MorphWordTest(unittest.TestCase):
		word = u'Пётр'
		
		def __init__(self, *args, **kwargs):
			super(MorphWordTest, self).__init__(*args, **kwargs)
			self.morph_word = self.word.replace(u'ё', u'е').upper()
		
		def testIt(self):
			assert(morph_word(self.word) == self.morph_word)

	class MorphTest(unittest.TestCase):
		
		def __init__(self, *args, **kwargs):
			super(MorphTest, self).__init__(*args, **kwargs)
		
		def setUp(self):
			self.morph = Morph()

	class BasicNamesTest(MorphTest):
		
		def testFirstNames(self):
			assert(self.morph.is_first_name(u'Петя'))
			assert(not self.morph.is_first_name(u'Пианино'))

	class GenderTest(MorphTest):
		testcase = [ (u'Владимир', u'мр'), (u'Дмитрий', u'мр'), (u'Людмила', u'жр'), (u'Светлана', u'жр') ]
		
		def testIt(self):
			for name, expected_tag in self.testcase:
				assert(self.morph.get_name_tags(name)[0] == expected_tag)

	class NormalFormTest(MorphTest):
		
		def testIt(self):
			names = [ 
				(u'Григория', u'Григорий'), 
				(u'Александра', u'Александр'), 
				(u'Василия', u'Василий'), 
				(u'Марии', u'Мария'), 
#				(u'Марине', u'Марина'),  
			]
			
			for broken_name, name in names:
				gender_tag, case = self.morph.get_name_tags(broken_name)
				assert(gender_tag)
				assert(case)
				assert(self.morph.normal_form(broken_name, gender_tag).capitalize() == name)

	class ExtractNamesTest(MorphTest):
		first_name_1 = u'Василий'
		middle_name_1 = u'Петрович'
		last_name_1 = u'Сковорода'
		
		first_name_2 = u'Петр'
		last_name_2 = u'Кастрюля'
		
		def __init__(self, *args, **kwargs):
			super(ExtractNamesTest, self).__init__(*args, **kwargs)
			
			self.test_phrase = u' '.join([ self.first_name_1, self.middle_name_1, self.last_name_1 ]) \
				+ u' зело любил когда ' \
				+ u' '.join([ self.first_name_2, self.last_name_2 ]) \
				+ u' к нему в гости заходит'
			
#			print self.test_phrase
		
		def testSetup(self):
			assert(self.morph.is_first_name(self.first_name_1))
			assert(not self.morph.is_first_name(self.last_name_1))
			assert(self.morph.is_first_name(self.first_name_2))
			assert(not self.morph.is_first_name(self.last_name_2))
		
		def testNamesExtract(self):
			names = identities(self.test_phrase)
			assert(len(names) == 2)
			for identity in names:
				capitalized = ' '.join(( word.capitalize() for word in identity.split(' ') ))
				assert((self.first_name_1 in capitalized and self.last_name_1 in capitalized) \
				or (self.first_name_2 in capitalized and self.last_name_2 in capitalized))
		
		def testWeirdStuff(self):
			testcases = [
				(u'По словам Бориса Абрамовича, это была их "общая идея" с Чемезовым', [ u'Абрамович Борис' ]),
				(u'В эпоху Владимира Путина Минтимер Шарипович прослыл', [ u'Путин Владимир', u'Шарипович Минтимер' ]),
#				(u'Список членов правления. Барков Анатолий Александрович.', [ u'Барков Анатолий' ]),
				(u'Федерального собрания Сергей Михайлович Миронов', [ u'Миронов Сергей' ]),
#				(u'его заместителя Валерия Малетина', [ u'Малетина Валерия' ]),  
			]
			
			for case, idents in testcases:
				gathered = identities(case)
#				for item in gathered:
#					print item
				assert(len(gathered) == len(idents))
				for ident in idents:
					assert(ident.upper() in gathered)

	class AmbiguityTest(MorphTest):
		
		def testSkipping(self):
			testcase = u'Катерина и Мария'
			assert(len(identities(testcase)) == 0)
			
		def testGeneral(self):
			testcases = [ 
				(u'Владиславом Каськивым', u'Каськив Владислав'),
				(u'Юлией Тимошенко', u'Тимошенко Юлия'),   
#				(u'Виктору Пшонке', u'Пшонка Виктор'),
#				(u'Александра Дония', u'Дония Александр'),
#				(u'Александр Доний', u'Дония Александр'),  
			]
			
			for text, ident in testcases:
				idents = identities(text)
				assert(len(idents) == 1)
				assert(' '.join(( word.capitalize() for word in idents[0].split(' ') )) == ident)
				
		def testMisoperations(self):
			testcases = [
				u'недоверие Кабмину Тимошенко', 
#				u'министру экономики в Кабмине Тимошенко',
				u'уже в ближайшие дни. Но Арсений отказался',
				u'Верховную Раду',
				u'Вчера Елисеев заявлял о том',
				u'Вчера Шуфрич выразил журналистам',
				u'Находящийся в Киеве Ричардсон заявил', 
			]
			
			for text in testcases:
				idents = identities(text)
				assert(len(idents) == 0)
	
		def testCaps(self):
			testcases = [ 
				(u'Бизнес Владимира Путина', u'Путин Владимир'), 
				(u'Диссертация Владимира Путина', u'Путин Владимир'),
				(u'Генпрокурора Михаила Поцоватого', u'Поцоватый Михаил'),
				(u'Блок Раисы Богатыревой', u'Богатырева Раиса'),
				(u'мэра Киева Леонида Черновецкого', u'Черновецкий Леонид'),
				(u'связей МВД в Киеве Александр Зарубицкий', u'Зарубицкий Александр'),
				(u'прокурор Киева Василий Присяжнюк', u'Присяжнюк Василий'),
				(u'премьер-министр Латвии Ивар Годманис', u'Годманис Ивар'), 
				(u'Президент Эстонии Томас Ильвес', u'Ильвес Томас'),
				(u'Президент Литвы Валдас Адамкус', u'Адамкус Валдас'),
				(u'образования и науки Ивана Вакарчука Об утверждении', u'Вакарчук Иван'),
#				(u'из-за амбиций премьер-министра Юлии Тимошенко Украина', u'Тимошенко Юлий'),
				(u'Печерского суда Киева Николай Голомша', u'Голомша Николай'),
#				(u'Биатлонисту сборной России Алексею Чурину', u'Чурин Алексей'),
			]
			
			for text, ident in testcases:
				idents = identities(text)
				assert(len(idents) == 1)
				assert(' '.join(( word.capitalize() for word in idents[0].split(' ') )) == ident)
		
		def testTitle(self):
			testcases = [ 
				(u'Президент Чечни Владимир Путин', u'Путин Владимир'), 
				(u'Президент Виктор Янукович', u'Янукович Виктор'),
				(u'Украины Виктор Ющенко', u'Ющенко Виктор'), 
				(u'Правительства Юлии Тимошенко', u'Тимошенко Юлий'),
				(u'президент России Борис Ельцин', u'Ельцин Борис'),
#				(u'главу своего Секретариата Виктора Балогу', u'Балог Виктор'), 
				(u'Верховной Рады Владимир Литвин', u'Литвин Владимир'),
				(u'посла России в Украине Виктора Черномырдина', u'Черномырдин Виктор'), 
				]
			
			for text, ident in testcases:
				idents = identities(text)
				assert(len(idents) == 1)
				assert(' '.join(( word.capitalize() for word in idents[0].split(' ') )) == ident)

	unittest.main()
