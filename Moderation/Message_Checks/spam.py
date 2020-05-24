from tools.read_write import read, write
default = True
check_name = 'Repeating content check'
name = 'spam'


def _is_repeating(message, repeating_count):
    for i in range(len(message) // repeating_count):
        m = message[:i + 1]

        if m == '':
            continue

        spammed_count = [0]
        for i in range(len(message) // len(m)):
            if message[i * len(m):(i + 1) * len(m)] == m:
                spammed_count[-1] += 1
            else:
                if spammed_count[-1] != 0:
                    spammed_count.append(0)
        if max(spammed_count) >= repeating_count:

            return True
    return False


async def check(message, ignore_chars=('\t\t', ' ')):
    content = message.content
    for c in ignore_chars:
        content = content.replace(c, '')
    guild = message.guild
    fd = await read('pl')
    if guild.id not in fd:
        fd[guild.id] = 10
        await write('pl', fd)
    repeating_count = fd[guild.id]
    message_new = ''
    for m in content:
        message_new += m
    content = message_new
    for i in range(len(content)):
        r = _is_repeating(content[i:], repeating_count)
        if r:
            return True
    return False
