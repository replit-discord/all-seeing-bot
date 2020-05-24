from tools.read_write import read, write
check_name = 'Ban word check'
default = True
name = 'banned_word'


converter_dict = {
    '\u0410': 'A', '\u0430': 'a',
    '\u0411': 'B', '\u0431': 'b',
    '\u0412': 'V', '\u0432': 'v',
    '\u0413': 'G', '\u0433': 'g',
    '\u0414': 'D', '\u0434': 'd',
    '\u0415': 'E', '\u0435': 'e',
    '\u0416': 'Zh', '\u0436': 'zh',
    '\u0417': 'Z', '\u0437': 'z',
    '\u0418': 'I', '\u0438': 'i',
    '\u0419': 'I', '\u0439': 'i',
    '\u041a': 'K', '\u043a': 'k',
    '\u041b': 'L', '\u043b': 'l',
    '\u041c': 'M', '\u043c': 'm',
    '\u041d': 'N', '\u043d': 'n',
    '\u041e': 'O', '\u043e': 'o',
    '\u041f': 'P', '\u043f': 'p',
    '\u0420': 'R', '\u0440': 'r',
    '\u0421': 'S', '\u0441': 's',
    '\u0422': 'T', '\u0442': 't',
    '\u0423': 'U', '\u0443': 'u',
    '\u0424': 'F', '\u0444': 'f',
    '\u0425': 'Kh', '\u0445': 'kh',
    '\u0426': 'Ts', '\u0446': 'ts',
    '\u0427': 'Ch', '\u0447': 'ch',
    '\u0428': 'Sh', '\u0448': 'sh',
    '\u0429': 'Shch', '\u0449': 'shch',
    '\u042a': '"', '\u044a': '"',
    '\u042b': 'Y', '\u044b': 'y',
    '\u042c': "'", '\u044c': "'",
    '\u042d': 'E', '\u044d': 'e',
    '\u042e': 'Iu', '\u044e': 'iu',
    '\u042f': 'Ia', '\u044f': 'ia',
    '\\u200': 'c'
}


ignored_chars = [
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
    'wipe'
    '',
    ''
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
                    for char in converter_dict:
                        mock_content.replace(char, converter_dict[char])
                    for char in ignored_chars:
                        mock_content.replace(char, '')
                    if p + a + s in mock_content:
                        bad_content = True

    if bad_content:

        return True
    else:
        return False
