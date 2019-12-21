import os
import discord
from datetime import datetime
from tools.read_write import read, write
from utils import index_args
from discord.ext import commands
from Moderation.spamchart import handle_infractions, handle_message, handle_banned_emoji


async def log(
	message,
	desc,
	title='**Moderation**',
	color=0xff0000,
	**kwargs
):

	guild = message.guild
	log_embed = discord.Embed(
		title=title,
		description=desc,
		color=color
	)
	for key, value in kwargs.items():
		if key == 'fields':
			for field in value:
				if len(field) == 2:
					log_embed.add_field(
						name=field[0],
						value=field[1]
					)
				else:
					log_embed.add_field(
						name=field[0],
						value=field[1],
						inline=field[2]
					)
		if key == 'showauth':
			if value:
				author = message.author
				disp_name = author.display_name
				icon_url = author.avatar_url
				log_embed.set_author(
					name=disp_name,
					icon_url=icon_url
				)
				log_embed.set_thumbnail(
					url=icon_url
				)
	now = datetime.now()
	log_embed.timestamp = now
	log_dict = await read('al')
	action_log_id = log_dict[guild.id]
	log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
	await log_channel.send(embed=log_embed)


async def get_checks(guild):
	full_check_list = await read('enabled_checks')
	changed = False
	guild_checks = full_check_list[guild.id]
	return guild_checks


class Checks(commands.Cog, name='Moderation Checks'):
	'''Customize checks everywhere or per channel!'''

	def cog_check(self, ctx):
		author = ctx.author
		if author.guild_permissions.administrator:
			return True
		else:
			return False

	def __init__(self, bot):
		self.bot = bot
		self.user = bot.user
		self.color = 0xd64c1e

	def list_checks(self):
		checks = os.listdir('./Moderation/Message_Checks')
		checks = [name[:-3] for name in checks]
		if '__pycach' in checks:
			checks.remove('__pycach')
		return checks

	async def check_enabled(self, guild, name, channel=None):
		guild_checks = await self.get_checks(guild)
		overides = guild_checks['Channel Overides']
		if channel is not None:
			if channel.id in overides:
				channel_checks = overides[channel.id]
				if name in channel_checks:
					return channel_checks[name]
				else:
					return guild_checks[name]
			else:
				return guild_checks[name]
		else:
			return guild_checks[name]

	async def set_checks(self, guild, data):
		full_list = await read('enabled_checks')
		full_list[guild.id] = data

		await write('enabled_checks', full_list)

	async def get_checks(self, guild):
		full_check_list = await read('enabled_checks')
		checks = self.list_checks()
		changed = False
		if guild.id in full_check_list:
			guild_checks = full_check_list[guild.id]
		else:
			changed = True
			guild_checks = {'Channel Overides': {}}
			for a in checks:
				directory = f'Moderation.Message_Checks.{a}'
				check = __import__(directory, globals(), locals(), [a])
				guild_checks[a] = check.default
		for a in checks:
			if a not in guild_checks:
				directory = f'Moderation.Message_Checks.{a}'
				changed = True
				check = __import__(directory, globals(), locals(), [a])
				guild_checks[a] = check.default
		await self.set_checks(guild, guild_checks)
		return guild_checks

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return
		if str(message.channel.type) != 'text':
			return
		await handle_message(message)
		author = message.author
		checks = self.list_checks()
		failed_check = False
		failed_checks = []
		cach_check = []
		guild = message.guild
		for l in checks:
			if '__pycach' in l:
				cach_check.append(l)

		for t in cach_check:
			checks.remove(t)

		for a in checks:
			failed = False
			# check_trust(author, a)

			directory = f'Moderation.Message_Checks.{a}'
			check = __import__(directory, globals(), locals(), [a])
			channel = message.channel
			enabled = await self.check_enabled(guild, a, channel)
			if enabled:

				failed = await check.check(message)
				if failed:
					failed_check = True
					failed_checks.append(check.check_name)
			del check

		if failed_checks != []:
			await handle_infractions(message, failed_checks)
			author = message.author
			if len(failed_checks) > 1:

				desc = '**Infractions:**\n'
				for check in failed_checks:
					desc += f'> **•** `{check}`\n'
			else:

				check = failed_checks[0]
				desc = f'<@{author.id}>\'s message was deleted because it failed the following check: `{check}`'
			fields = [('**Message Content**', message.content)]
			await log(
				message,
				desc,
				showauth=True,
				fields=fields
			)
			
			await message.delete()
			await author.send('Your message was deleted, because it was spam or contained a word banned on the guild.')

	@commands.Cog.listener()
	async def on_raw_message_edit(self, payload):
		guild = self.bot.get_guild(int(payload.data['guild_id']))

		channel = guild.get_channel(int(payload.data['channel_id']))

		message = await channel.fetch_message(int(payload.data['id']))
		if message.author == self.bot.user:
			return

		if str(message.channel.type) == 'text':
			checks = self.list_checks()
			failed_check = False
			failed_checks = []
			cach_check = []

			for l in checks:
				if '__pycach' in l:
					cach_check.append(l)

			for t in cach_check:
				checks.remove(t)

			for a in checks:
				failed = False

				directory = f'Moderation.Message_Checks.{a}'
				check = __import__(directory, globals(), locals(), [a])

				enabled = await self.check_enabled(guild, a, channel)
				if enabled:

					failed = await check.check(message)
					if failed:
						failed_check = True
						failed_checks.append(check.check_name)
				del check
			if failed_checks != []:
				await handle_infractions(message, failed_checks)
				author = message.author
				if len(failed_checks) > 1:

					desc = f'<@{author.id}>\'s message was automatically deleted.\n**Infractions:**\n'
					for check in failed_checks:
						desc += f'> **•** `{check}`\n'
				else:

					check = failed_checks[0]
					desc = f'<@{author.id}>\'s message was deleted because it failed the following check: `{check}`'
				fields = [('**Message Content**', message.content)]
				await log(
					message,
					desc,
					showauth=True,
					fields=fields
				)
				await message.delete()
				await author.send('Your message was deleted, because it was spam or contained a word banned on the guild.')

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		guild_id = payload.guild_id
		banned_reactions = await read('banEmojis')
		if guild_id in banned_reactions:
			if payload.emoji in banned_reactions[guild_id]:

				guild_id = payload.guild_id
				channel_id = payload.channel_id
				guild = self.bot.get_guild(guild_id)
				msg_id = payload.message_id

				channel = guild.get_channel(channel_id)
				msg = await channel.fetch_message(msg_id)
				reactions = msg.reactions
				for r in reactions:
					if r.emoji == payload.emoji:
						for user in r.users:
							r.remove(user)
							handle_banned_emoji(r, user)

	@commands.command(name='enablecheck', aliases=['echeck'])
	async def enable_check(self, ctx, check, *argv):
		'''

		Enable a check. For the entire server by default.
		-c Enable for specified channel. Uses current channel if none specified.
		Example Usage:
		``````css
		?ec repeating content check -g  // Enables spam check globally
		``````css
		?ec banned content check -c #channel  // Enables banned content check in #channel
		```
		'''
		check = check.lower()
		guild = ctx.guild
		guild_checks = await self.get_checks(ctx.guild)
		args = index_args(argv)
		extended_name = ' '.join(args[0])
		check += f' {extended_name}'
		args = args[1:]
		channel_selected = False
		checks = self.list_checks()
		check_dict = {}
		for a in checks:
			directory = f'Moderation.Message_Checks.{a}'
			f = __import__(directory, globals(), locals(), [a])

			name = f.check_name
			check_dict[name.lower()] = a
			del f
		if check in check_dict:
			for info in args:
				if info[0] == '-c':
					if len(info) != 1:
						channel = commands.TextChannelConverter()
						channel = await channel.convert(ctx, info[1])
						channel_selected = True
					else:
						channel = ctx.channel
						channel_selected = True

			if channel_selected:
				overides = guild_checks['Channel Overides']
				if channel.id in overides:
					channel_overides = overides[channel.id]
				else:
					channel_overides = {}
				channel_overides[check_dict[check]] = True
				overides[channel.id] = channel_overides
				guild_checks['Channel Overides'] = overides
			else:
				guild_checks[check_dict[check]] = True
			await self.set_checks(guild, guild_checks)

	@commands.command(name='disablecheck', aliases=['dcheck'])
	async def disable_check(self, ctx, check, *argv):
		'''

		Disable a check. For the entire server by default.
		-c Disable for specified channel. Uses current channel if none specified.
		Example Usage:
		``````css
		?dc repeating content check -g  // Disable spam check globally
		``````css
		?dc banned content check -c #channel  // Disable banned content check in #channel
		```
		'''
		check = check.lower()
		guild = ctx.guild
		guild_checks = await self.get_checks(ctx.guild)
		args = index_args(argv)
		extended_name = ' '.join(args[0])
		check += f' {extended_name}'
		args = args[1:]
		channel_selected = False
		checks = self.list_checks()
		check_dict = {}
		for a in checks:
			directory = f'Moderation.Message_Checks.{a}'
			f = __import__(directory, globals(), locals(), [a])

			name = f.check_name
			check_dict[name.lower()] = a
			del f
		if check in check_dict:
			for info in args:
				if info[0] == '-c':
					if len(info) != 1:
						channel = commands.TextChannelConverter()
						channel = await channel.convert(ctx, info[1])
						channel_selected = True
					else:
						channel = ctx.channel
						channel_selected = True

			if channel_selected:
				overides = guild_checks['Channel Overides']
				if channel.id in overides:
					channel_overides = overides[channel.id]
				else:
					channel_overides = {}
				channel_overides[check_dict[check]] = False
				overides[channel.id] = channel_overides
				guild_checks['Channel Overides'] = overides
			else:
				guild_checks[check_dict[check]] = False
			await self.set_checks(guild, guild_checks)

	@commands.command(name='listchecks', aliases=['lc'])
	async def guild_checks(self, ctx, channel: discord.TextChannel = None):
		'''List enabled and disabled checks.
		Example Usage:
		``````css
		?lc // Gets the defalt checks for the server.
		``````css
		?lc #​channel // Get checks in #​channel
		```
		'''
		guild = ctx.guild
		checks = self.list_checks()

		if channel is None:
			channel = ctx.channel

		desc = '```css\n'
		for a in checks:
			enabled = await self.check_enabled(guild, a, channel)
			directory = f'Moderation.Message_Checks.{a}'
			check = __import__(directory, globals(), locals(), [a])

			name = check.check_name
			del check
			name += ':'
			name = name.ljust(30, ' ')
			if enabled:
				name.ljust
				desc += name + '✅\n'


			else:
				length = len(name) + 2
				space_lenght = 30 - length
				spaces = space_lenght * ' '
				desc += name + '❌\n'
		desc += '```'
		await ctx.send(desc)


def setup(bot):

	bot.add_cog(Checks(bot))
