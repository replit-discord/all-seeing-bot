from tools.read_write import read, write
check_name = 'Mention limit check'
default = True
name = 'mention_spam'


async def check(message):
    guild = message.guild
    fd = await read('ml')
    if guild.id not in fd:
        fd[guild.id] = 30
        await write('ml', fd)
    mention_limit = fd[guild.id]
    mentions = message.mentions
    mentions += message.role_mentions
    if len(mentions) > mention_limit:
        failed_check = True
    else:
        failed_check = False
    return failed_check
