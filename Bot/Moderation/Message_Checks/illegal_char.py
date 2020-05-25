import re

default = False
check_name = 'Illegal character check'
name = 'illegal_char'
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
emoji_pattern = re.compile(
    "["
    u"\U0001F600-\U0001F64F"
    u"\U0001F300-\U0001F5FF"
    u"\U0001F680-\U0001F6FF"
    u"\U0001F1E0-\U0001F1FF"
    "]+",
    flags=re.UNICODE
)


async def check(message):
    content = message.content
    content = emoji_pattern.sub(r'', content)

    for character in ignoredChars:
        content = content.replace(character, '')
    try:
        yesAnnotherThing = str(repr(content).encode('ascii'))
    except UnicodeEncodeError:
        return True
    return content not in (yesAnnotherThing).replace('\\n', '\n')
