from tools.read_write import read, write
from ctypes import Structure, pointer, POINTER, c_void_p, c_longlong, c_char, c_char_p, cdll, cast
check_name = 'Ban word check'
default = True
name = 'banned_word'


class Word(Structure):
    _fields_ = [
        ('paranoid', c_char),
        ('word', c_char_p)
    ]


class GoSlice(Structure):
    _fields_ = [
        ('data', POINTER(c_void_p)),
        ('len', c_longlong),
        ('cap', c_longlong)
    ]


filter = cdll.LoadLibrary('../Filter/libfilter.so')


async def check(message):
    print('start')
    content = message.content.lower()
    guild = message.guild
    fd = await read('banWords', True, False)
    newFd = {}
    for g in fd:
        guild_data = fd[g]
        new_guild_data = []
        for w in guild_data:
            if not isinstance(w, str):
                new_guild_data.append(w)
                continue

            new_guild_data.append({
                'word': w,
                'paranoia': 1
            })

        newFd[g] = new_guild_data

    await write('banWords', newFd, False)

    fd = await read('banWords', True, False)

    if guild.id not in fd:
        fd[guild.id] = []
        await write('banWords', fd, False)

    ban_words = fd[guild.id]

    c_words = []

    for w in ban_words:
        print('word', bytes(w['word'], 'utf-8'))
        print('paranoia', w['paranoia'])
        c_words.append(cast(
            pointer(
                Word(
                    w['paranoia'],
                    bytes(w['word'], 'utf-8'),
                )
            ),
            c_void_p)
        )

    sliceData = (c_void_p * len(c_words))(*c_words)

    data = GoSlice(sliceData, len(c_words), len(c_words))
    print(bytes(message.content, 'utf-8'))
    result = filter.check(bytes(message.content, 'utf-8'), data)

    print(result)

    return result == True
