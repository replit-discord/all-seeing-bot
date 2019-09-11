from rw import read

ignoredChars = [
	'`',
	'*',
	'-',
	'~',
	'_',
	'|',
	'\'',
	'\\',
	'\n',
	'​',
	'”',
	'"'
]

prefixes = [
	'dumb',
	'mother',
	'god',
	'gosh',
	'jack',
	''
]

suffixes = [
	'ing',
	'er',
	'it',
	'hat',
	''
]

base_words = [

	'fuck',
	'cum',
	'nig' + 'ger',
	'damn',
	'motherfucker',
	'shit',
	'ass',
	'dick',
	'bitch',
	'cunt'

]

blacklist_suffixes = [
	'assinate',
	'inate',
	'assin',
	'in'
]


async def banned_content_check(message):
	content = message.content
	guild = message.guild

	full_ban_list = await read('banWords', True, False)
	ban_words = full_ban_list[guild.id]
	content.replace(' ', '')
	bad_content = False
	if len(ban_words) > 0:
		for a in ban_words:
			for p in prefixes:
				for s in suffixes:
					mock_content = content
					for b in blacklist_suffixes:
						while p + a + s + b in mock_content:
							mock_content = mock_content.replace(p + a + s + b, '')

					if p + a + s in mock_content:
						bad_content = True
	if bad_content:

		return True
	else:
		return False
