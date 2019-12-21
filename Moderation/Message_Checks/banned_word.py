from tools.read_write import read, write
check_name = 'Ban word check'
default = True

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
	'"',
	'‍',
	'‌',
	'‎',
	'‏'
]

prefixes = [
	'dumb',
	'mother',
	'god',
	'gosh',
	'jack',
	'mega',
	''
]

suffixes = [
	'ing',
	'er',
	'it',
	'hat',
	'wipe',
	'wipe',
	'',
]

base_words = [

	'fuck',
	'cum',
	'nig' + 'ger',
	'shit',
	'ass',
	'dick',
	'bitch',
	'cunt',
	'faggot'

]


async def check(message):
	print('start')
	content = message.content.lower()
	guild = message.guild
	fd = await read('banWords', True, False)
	if guild.id not in fd:
		fd[guild.id] = []
		await write('banWords', fd, False)
	ban_words = fd[guild.id]

	content = content.replace('assassinate', '')
	content = content.replace('assassin', '')
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
