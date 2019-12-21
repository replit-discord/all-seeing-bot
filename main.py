import os
import discord
import asyncio
from keep_alive import keep_alive
from discord.ext import commands
from background_tasks import bg_tasks
bot = commands.Bot(
	command_prefix='?',
	case_insensitive=True
)

# regex to find all print statements \n\s*print\([^()]*\)
class initialized:
	def __init__(self):
		self.started = False

	def __call__(self):
		if not self.started:
			self.started = True
			return False
		else:
			return True

started = initialized()

extensions = [
	'Commands.dev_cmds',
	'Commands.data_tweaking',
	# 'Starboard.main',
	'Commands.moderation',
	'Moderation.main',
	'Commands.fun',
	'Commands.help',
	'Mail.main'
]

if __name__ == '__main__':
	for extension in extensions:
		bot.load_extension(extension)


@bot.event
async def on_ready():
	await bot.change_presence(
		activity=discord.Activity(
			name='everything', type=discord.ActivityType(3)
		)
	)
	if not started():
		await asyncio.create_task(bg_tasks(bot))
	print('ready')

keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)
