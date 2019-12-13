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
	'wipe',
	'es'
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


async def banned_content_check(message):
	content = message.content
	guild = message.guild
	content = content.replace('assassinate', '')
	content = content.replace ('assassin', '')
	full_ban_list = await read('banWords', True, False)
	ban_words = full_ban_list[guild.id]
	content.replace(' ', '')
	bad_content = False
	if len(ban_words) > 0:
		for a in ban_words:
			for p in prefixes:
				for s in suffixes:
					mock_content = content
					mock_content.replace('4', 'a')
					mock_content.replace('3', 'e')
					mock_content.replace('0', 'o')

					if p + a + s in mock_content:
						bad_content = True
	if bad_content:

		return True
	else:
		return False
