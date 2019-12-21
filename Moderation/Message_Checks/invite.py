
check_name = 'Invite link check'
default = False


async def check(message):
	has_link = any(url in message.content for url in [
		'discord.gg/', 'discordapp.com/invite/']
	)
	return has_link
