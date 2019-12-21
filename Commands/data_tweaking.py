import discord
from datetime import datetime
from discord.ext import commands
from tools.read_write import read, write
from utils import InvalidDate, find_date



class Customization(commands.Cog, name='Customization'):
	'''Customization commands'''
	def __init__(self, bot):
		self.bot = bot
		self.color = 0x3219d1

	async def log(self, ctx, desc, title='**Customization**', color=0x00ff80):
		guild = ctx.guild
		log_embed = discord.Embed(
			title=title,
			description=desc,
			color=color
		)
		now = datetime.now()
		log_embed.timestamp = now
		log_dict = await read('al')
		author = ctx.author
		disp_name = author.display_name
		icon_url = author.avatar_url
		log_embed.set_author(
			name=disp_name,
			icon_url=icon_url
		)
		log_embed.set_thumbnail(
			url=icon_url
		)
		action_log_id = log_dict[guild.id]
		log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
		await log_channel.send(embed=log_embed)

	def cog_check(self, ctx):
		user = ctx.author
		admin = user.guild_permissions.administrator
		return admin

	@commands.command(name='trustrole', aliases=['tr'])
	async def trust_role(self, ctx, role: discord.Role):
		'''Trust a role.'''
		guild = ctx.guild
		author = ctx.author
		channel = ctx.channel

		trust_roles = await read('td')

		if guild.id not in trust_roles:
			guild_trust_roles = []

		else:
			guild_trust_roles = trust_roles[guild.id]

		if role.id not in guild_trust_roles:
			guild_trust_roles.append(role.id)
			await channel.send('Role has been trusted.')
			trust_roles[guild.id] = guild_trust_roles
			await write('td', trust_roles)

			log_msg = str(f'<@{author.id}> trusted role `{role.name}`')

			await self.log(ctx, log_msg, 'Trust')
		else:
			await channel.send('Role is already trusted!')

	@commands.command(name='untrustrole', aliases=['utr'])
	async def un_trust_role(self, ctx, role: discord.Role):
		'''Un-trust a role.'''
		guild = ctx.guild
		author = ctx.author
		channel = ctx.channel

		trust_roles = await read('td')

		if guild.id not in trust_roles:
			guild_trust_roles = []

		else:
			guild_trust_roles = trust_roles[guild.id]

		if role.id in guild_trust_roles:
			guild_trust_roles.remove(role.id)
			await channel.send('Role has been untrusted.')
			trust_roles[guild.id] = guild_trust_roles
			await write('td', trust_roles)

			log_msg = str(f'<@{author.id}> untrusted role `{role.name}`')

			await self.log(ctx, log_msg, 'Trust')
		else:
			await channel.send('Role is not trusted!')

	@commands.command(name='muterole', aliases=['mr', 'smr'])
	async def set_mute_role(self, ctx, role=discord.Role):
		'''Set the role the bot gives to mute users.
		Example Usage:
		``````css
		?smr @‎Muted // Sets muted role to @‎Muted
		``````css
		?smr 123456789012345 // Sets muted role to match role with id 123456789012345
		```'''
		guild = ctx.guild
		author = ctx.author
		channel = ctx.channel

		mute_roles = await read('mute-role-id')

		mute_roles[guild.id] = role.id
		await channel.send('Mute role has been set.')

		await write('mute-role-id', mute_roles)

		log_msg = str(f'<@{author.id}> set the muted role to `{role.name}`')

		await self.log(ctx, log_msg, 'Customization')

	@commands.command(name='setoffenseduration', aliases=['od', 'sod'])
	async def set_offense_duration(self, ctx, time: str = None):
		'''Set the server offense duration.'''
		guild = ctx.guild
		author = ctx.author
		offense_duration = await read('od')

		if time is None:
			if guild.id in offense_duration:
				seconds = offense_duration[guild.id]
				await ctx.send(f'The current offense duration is `{seconds}`')
			else:
				await ctx.send('No offense duration set!')

		else:
			try:
				seconds = int(time)
				found_time = True

			except ValueError:
				found_time = False

			try:
				if not found_time:
					time = find_date(time)
					seconds = time.total_seconds()
				offense_duration[guild.id] = seconds
				await write('od', offense_duration)
				await self.log(ctx, f'<@{author.id}> set the offense duration to {time}')

			except InvalidDate:
				await ctx.send(f'Invalid ammount of time, `{time}`.')

	@commands.command(name='setmuteduration', aliases=['md', 'smd'])
	async def set_mute_duration(self, ctx, time: str = None):
		'''Set the default mute duration.'''
		guild = ctx.guild
		author = ctx.author
		mute_duration = await read('md')

		if time is None:
			if guild.id in mute_duration:
				seconds = mute_duration[guild.id]
				await ctx.send(f'The current default mute duration is `{seconds}`')
			else:
				await ctx.send('No default mute duration set!')

		else:
			try:
				seconds = int(time)
				found_time = True

			except ValueError:
				found_time = False

			try:
				if not found_time:
					time = find_date(time)
					seconds = time.total_seconds()
				mute_duration[guild.id] = seconds
				await write('md', mute_duration)
				await self.log(
					ctx,
					f'<@{author.id}> set the default mute duration to {time}'
				)

			except InvalidDate:
				await ctx.send(f'Invalid ammount of time, `{time}`.')

	@commands.command(name='offenselimit', aliases=['ol', 'sol'])
	async def set_offense_limit(self, ctx, ammount: int = None):
		'''Set the server's offense limit.'''
		guild = ctx.guild
		author = ctx.author
		offense_limits = await read('ol')

		if ammount is not None:
			offense_limits[guild.id] = ammount
			await ctx.send(f'Offense limit has been set to `{ammount}`.')
			await self.log(
				ctx,
				f'<@{author.id}> set the offense limit to `{ammount}`.'
			)
		else:
			if guild.id in offense_limits:
				current_limit = offense_limits[guild.id]
				await ctx.send(f'The current offense limit is `{current_limit}')
			else:
				await ctx.send('The server offense limit is not set!')

	@commands.command(name='emojimax', aliases=['em'])
	async def set_emoji_max(self, ctx, ammount: int = None):
		'''Set the guilds emoji max (per message).'''
		guild = ctx.guild
		author = ctx.author
		emoji_max = await read('em')

		if ammount is not None:
			emoji_max[guild.id] = ammount
			await ctx.send(f'Emoji max has been set to `{ammount}`.')
			await self.log(
				ctx,
				f'<@{author.id}> set the emoji max to `{ammount}`.'
			)
			await write('em', emoji_max)
		else:
			if guild.id in emoji_max:
				current_limit = emoji_max[guild.id]
				await ctx.send(f'The current emoji max is `{current_limit}')
			else:
				await ctx.send('The server emoji max is not set!')

	@commands.command(name='mentionlimit', aliases=['ml'])
	async def set_mention_limit(self, ctx, ammount: int = None):
		'''Set the maximum ammount of @‏‏‎mentions per message'''
		guild = ctx.guild
		author = ctx.author
		mention_limit = await read('ml')

		if ammount is not None:
			mention_limit[guild.id] = ammount
			await ctx.send(f'Mention limit has been set to `{ammount}`.')
			await self.log(
				ctx,
				f'<@{author.id}> set the mention limit to `{ammount}`.'
			)
			await write('ml', mention_limit)
		else:
			if guild.id in mention_limit:
				current_limit = mention_limit[guild.id]
				await ctx.send(f'The current mention limit is `{current_limit}')
			else:
				await ctx.send('The server mention limit is not set!')

	@commands.command(name='muteincrement', aliases=['mi'])
	async def set_mute_inc(self, ctx, ammount: int = None):
		'''Set the mute increment for users.ammount'''
		guild = ctx.guild
		author = ctx.author
		mute_increment = await read('mi')

		if ammount is not None:
			mute_increment[guild.id] = ammount
			await ctx.send(f'mute increment has been set to `{ammount}`.')
			await self.log(
				ctx,
				f'<@{author.id}> set the mute increment to `{ammount}`.'
			)
			await write('mi', mute_increment)
		else:
			if guild.id in mute_increment:
				current_limit = mute_increment[guild.id]
				await ctx.send(f'The current mute increment is `{current_limit}')
			else:
				await ctx.send('The server mute increment is not set!')

	@commands.command(name='phraselimit', aliases=['pl', 'sm'])
	async def set_phrase_limit(self, ctx, ammount: int = None):
		'''Set the maximum ammount of times a phrase can repeat in a message'''
		guild = ctx.guild
		author = ctx.author
		phrase_limit = await read('pl')

		if ammount is not None:
			phrase_limit[guild.id] = ammount
			await ctx.send(f'phrase limit has been set to `{ammount}`.')
			await self.log(
				ctx,
				f'<@{author.id}> set the phrase limit to `{ammount}`.'
			)
			await write('pl', phrase_limit)
		else:
			if guild.id in phrase_limit:
				current_limit = phrase_limit[guild.id]
				await ctx.send(f'The current phrase limit is `{current_limit}`')
			else:
				await ctx.send('The server phrase limit is not set!')

	@commands.command(name='actionlog', aliases=['al'])
	async def set_action_log(self, ctx, log_channel: discord.TextChannel = None):
		'''Set the server's action log channel.'''
		guild = ctx.guild
		author = ctx.author
		log_channels = await read('al')

		if log_channel is None:
			log_channel = ctx.channel
		await ctx.send('Action log channel has been set')
		log_channels[guild.id] = log_channel.id
		await write('al', log_channels)
		await self.log(
			ctx,
			f'<@{author.id}> set the action log channel to <#{log_channel.id}>.'
		)

	@commands.command(name='modmail', aliases=['mm'])
	async def set_mail_channel(
		self,
		ctx,
		mail_channel: discord.TextChannel = None
	):
		'''Set the server's mod mail channel.'''
		guild = ctx.guild
		author = ctx.author
		mail_channels = await read('mod_mail')

		if mail_channel is None:
			mail_channel = ctx.channel
		await ctx.send('Mod mail channel has been set')
		if guild.id in mail_channels:
			mail_channels[guild.id]['Channel'] = mail_channel.id
		else:
			mail_channels[guild.id] = {'Channel': mail_channel.id}
		await write('mod_mail', mail_channels)
		await self.log(
			ctx,
			f'<@{author.id}> set the mod mail channel to <#{mail_channel.id}>.'
		)


def setup(bot):
	bot.add_cog(Customization(bot))
