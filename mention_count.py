import discord


async def mention_count(message):
	return int(len(message.mentions))