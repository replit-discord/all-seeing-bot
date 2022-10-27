
check_name = 'Discord server invite link check'
default = False
name = 'invite'


async def check(message):
    has_link = any(url in message.content for url in [
        'discord.gg/', 'discordapp.com/invite/', 'discord.com/invite']
    )
    return has_link
