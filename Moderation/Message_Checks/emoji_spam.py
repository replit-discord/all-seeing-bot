import re
import emoji
from tools.read_write import read, write
check_name = 'Emoji max check'
default = True
name = 'emoji_spam'


async def check(message):
    content = message.content
    guild = message.guild
    fd = await read('em')
    if guild.id not in fd:
        fd[guild.id] = 30
        await write('em', fd)
    emoji_max = fd[guild.id]
    emoji_list = [c for c in content if c in emoji.UNICODE_EMOJI]
    emoji_list += re.findall(r'<:\w*:\d*>', content)
    if len(emoji_list) > emoji_max:
        failed_check = True
    else:
        failed_check = False
    return failed_check
