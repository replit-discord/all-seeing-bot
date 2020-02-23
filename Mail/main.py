import asyncio
import discord
from utils import find_date
from datetime import datetime
from discord.ext import commands
from tools.read_write import read, write


class PendingConversation:
	def __init__(self, user_id, guild_id):
		self.user_id = user_id
		self.guild_id = guild_id
	
	async def open(self, mod_id, bot):
		guild = bot.get_guild(self.guild_id)
		user = guild.get_member(self.user_id)
		await user.send('Your request has been opened.')
		return Conversation(
			self.user_id,
			mod_id,
			self.guild_id
		)


class OpenConverstions:
	def __init__(self):
		self.conversations = []

	def __repr__(self):
		return self.conversations

	def append(self, conv):
		self.conversations.append(conv)


class PendingConversationList:
	def __init__(self):
		self.data = {}
		self.users = []

	def __repr__(self):
		return self.data

	def get_data(self, message_id):
		if message_id in self.data:
			return self.data[message_id]
		else:
			return None

	def add_data(self, ctx, message):
		user = ctx.author
		if user.id in self.users:
			return False
		guild = message.guild

		self.data[message.id] = PendingConversation(user.id, guild.id)
		self.users.append(user.id)
		return True

	def remove(self, message):
		if message.id not in self.data:
			return
		else:
			user_id = self.data[message.id].user_id
			del self.data[message.id]
			self.users.remove(user_id)


async def check_guild(user, guild):
	banned_users = await get_banned_users(guild)
	if banned_users is None:
		return False
	if user.id in banned_users:
		return False
	if user in guild.members:
		return True
	return False

pending = PendingConversationList()
open_converstions = OpenConverstions()

async def get_channel(guild):
		mod_mail = await read('mod_mail')
		channel_id = mod_mail[guild.id]['Channel']
		return guild.get_channel(channel_id)

class Conversation:
	def __init__(self, user_id, mod_id, guild_id):

		self.user_id = user_id
		self.guild_id = guild_id
		self.mod_id = mod_id
		self.expire_date = find_date('5h')

	async def get_objects(self, bot):
		self.guild = bot.get_guild(self.guild_id)
		self.user = self.guild.get_member(self.user_id)
		self.mod = self.guild.get_member(self.mod_id)
		self.channel = await get_channel(self.guild)
		self.initialized = True
	
	def check_channel(self, message):
		channel = message.channel
		if isinstance(channel, discord.DMChannel):
			return channel.recipient.id == self.user.id
		return channel == self.channel
			
	def check_message(self, message):
		if not self.check_channel(message):
			return
		author = message.author

		return author.id == self.user_id or author.id == self.mod_id
	
	async def send_to_guild(self, message):
		channel = self.channel
		embed = discord.Embed(
			title=self.user.display_name,
			description=message.content,
			color=0x256bdb
		)
		embed.set_author(
			name=message.author.display_name,
			icon_url=message.author.avatar_url
		)
		embed.timestamp = message.created_at
		await channel.send(f'<@{self.mod_id}>', embed=embed)
		
	async def send_to_user(self, message):
		embed = discord.Embed(
			title='Moderator',
			description=message.content,
			color=0x256bdb
		)
		embed.timestamp = message.created_at
		await self.user.send(embed=embed)

	async def handle_message(self, message):
		if not self.check_message(message):
			return False
		author = message.author

		if author.id == self.user.id:
			await self.send_to_guild(message)
		
		else:
			await self.send_to_user(message)
		return True


async def get_banned_users(guild):
	try:
		mod_mail_data = (await read('mod_mail'))[guild.id]
	except KeyError:
		return None
	if 'Banned Users' in mod_mail_data:
		banned_users = mod_mail_data['Banned Users']
	else:
		banned_users = []
	return banned_users


async def set_banned_users(guild, banned_users: list):
	mod_mail_data = (await read('mod_mail'))[guild.id]
	mod_mail_data['Banned Users'] = banned_users
	mod_mail = await read('mod_mail')
	mod_mail[guild.id] = mod_mail_data
	await write('mod_mail', mod_mail)


class user:

	def __init__(self, user):
		self.user = user

	async def check_user(self):
		user = self.user
		mod_mail = await read('mod_mail')
		users = mod_mail['users']
		return user.id in users

	async def __call__(self):
		user = self.user
		mod_mail = await read('mod_mail')
		users = mod_mail['users']
		return users[user.id]
	
	def __repr__(self):
		user = self.user
		loop = asyncio.get_event_loop()
		mod_mail = loop.run_until_complete(read('mod_mail'))
		users = mod_mail['users']
		return users[user.id]


class mod:

	def __init__(self, ctx):
		self.user = ctx.author
		self.guild = ctx.guild

	async def check_user(self):
		user = self.user
		mod_mail = await read('mod_mail')
		users = mod_mail['mods']
		return user.id in users

	async def __call__(self):
		user = self.user
		mod_mail = await read('mod_mail')
		users = mod_mail['mods']
		return users[user.id]
	
	def __repr__(self):
		user = self.user
		loop = asyncio.get_event_loop()
		mod_mail = loop.run_until_complete(read('mod_mail'))
		users = mod_mail['mods']
		return users[user.id]

def is_private(ctx):
	return isinstance(ctx.channel, discord.DMChannel)

class ModMail(commands.Cog, name='Mod Mail'):
	'''Commands for a mod mail system'''
	def __init__(self, bot):
		self.bot = bot
		self.color = 0x11bed9

	def readcheck(self, ctx):
		return ctx.author.guild_permissions.administrator

	'''def cog_check(ctx):
		channel = ctx.channel
		return channel.type == 'private' '''

	@commands.Cog.listener()
	async def on_message(self, message):

	
		if message.author == self.bot.user:
			return
		for conv in open_converstions.conversations:
			if await conv.handle_message(message):
				return
		author = message.author
		if str(message.channel.type) == 'private':
			if message.content[1:].startswith('mail'):
				return
			guild_list = [
				guild for guild in self.bot.guilds if (await check_guild(
					author,
					guild
				))
			]
			desc = 'Please use `?mail <guild number> to send a message to that guild.\n'
			for n in range(len(guild_list)):
				guild = guild_list[n]
				desc += f'\n\n{n+1}: {guild.name}'
			embed = discord.Embed(
				title="Guilds",
				description=desc,
				color=0xff00dd
			)
			embed.set_footer(
				text='Server not showing? You are either banned from mod mail on it '
				'or the server doesnt not have mod mail setup yet.'
			)
			await author.send(embed=embed)
			return


	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		message = reaction.message
		if message.id not in pending.data:
			return
		if user.guild_permissions.administrator:
			if reaction.emoji == '✅':
				conv = await pending.data[message.id].open(user.id, self.bot)
				await conv.get_objects(self.bot)
				open_converstions.append(conv)
			elif reaction.emoji == '❌':
				pending.remove(message)
			elif str(reaction.emoji) == '<:ban_hammer:655098586010353695>':
				banned_users = await get_banned_users(reaction.message.guild)
				banned_users.append(pending.data[message.id].user_id)
				pending.remove(message)
				await set_banned_users(reaction.message.guild, banned_users)
				
				

	@commands.command(name='mail')
	@commands.check(is_private)
	async def mail(self, ctx, server: int, *argv):
		'''Send a message to a server.
		```css
		Example Usage:
		``````css
		?mail <server number> hi // Make a ticket on the correrlating server with the content hi```
		'''
		author = ctx.author
		content = ' '.join(argv)
		guild = [
			guild for guild in self.bot.guilds if (await check_guild(
				author,
				guild
			))
		][server-1]
		channel = await get_channel(guild)
		embed = discord.Embed(
			title=ctx.author.display_name,
			description=content,
			color=0x256bdb
		)
		embed.set_author(
			name=ctx.author.display_name,
			icon_url=ctx.author.avatar_url
		)
		embed.timestamp = ctx.message.created_at
		message = await channel.send(embed=embed)
		is_added = pending.add_data(ctx, message)
		if is_added:
			await message.add_reaction('✅')
			await message.add_reaction('❌')
			await message.add_reaction(
				'<:ban_hammer:655098586010353695>'
			)
	
	@commands.command(name='munban', aliases=['mu'])
	@commands.has_permissions(administrator=True)
	async def unban(self, ctx, user: discord.Member):
		'''Unban a user from usage of the server's mod mail system.
		```css
		Example Usage:
		``````css
		?munban @<user> // Allow @<user> access to the server's mod mail system.AttributeError```'''
		banned_users = await get_banned_users(ctx.guild)
		if user.id not in banned_users:
			await ctx.send(f'<@{user.id}> is not banned from this servers mod mail system!')
			return
		banned_users.remove(user.id)
		await set_banned_users(ctx.guild, banned_users)
		await ctx.send(f'<@{user.id}> has been unbanned from the server\'s mod mail system.')

		
def setup(bot):
	bot.add_cog(ModMail(bot))