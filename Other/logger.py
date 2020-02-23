import discord
from tools.read_write import read, write
from discord.ext import commands
from discord import AuditLogAction
from datetime import datetime, time

defaults = {
	'edits': True,
	'deletes': True,
	'bans': True,
	'kicks': True,
	'bulkdelete': True,
	'joins': True,
	'leaves': False
}


async def log(
	message,
	desc,
	timestamp,
	title='**Message Log**',
	color=0xff0000,
	**kwargs
):

	idk = False
	log_embed = discord.Embed(
		title=title,
		description=desc,
		color=color
	)
	print('fine1')
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
		if key == 'show_user':
			author = value
			disp_name = author.display_name
			icon_url = author.avatar_url
			log_embed.set_author(
				name=disp_name,
				icon_url=icon_url
			)
		if key == 'no_msg':
			guild = value
			idk = True
	print('fine2')
	if not idk:
		guild = message.guild
	log_embed.timestamp = timestamp
	log_dict = await read('al')
	print('fine3')
	action_log_id = log_dict[guild.id]
	log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
	print('fine4')
	await log_channel.send(embed=log_embed)
	print('fine5')


class Logger(commands.Cog, name='Logs'):
	def __init__(self, bot):
		self.bot = bot
		self.color = 0x000000

	async def cog_check(self, ctx):
		if ctx.guild is None:
			return False

	async def check_log(self, name, guild):
		logger_dict = await read('logger_dict')
		if guild.id not in logger_dict:
			guild_dict = {}
		else:
			guild_dict = logger_dict[guild.id]
		if name in guild_dict:
			return guild_dict[name]
		else:
			return defaults[name]

	def other_checks(self, message):
		channel = message.channel
		author = message.author
		return isinstance(channel, discord.TextChannel) and not author.bot

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		guild = after.guild
		if not (await self.check_log('edits', guild)):
			return
		if not self.other_checks(after):
			return
		author = after.author
		desc = f'<@{author.id}> edited their message.'
		fields = [
			('**Before**', before.content, True),
			('**After**', after.content, True)
		]
		timestamp = after.edited_at
		await log(
			after,
			desc,
			timestamp,
			'**Message edit**',
			0x42f5a1,
			fields=fields,
			showauth=True
		)

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		guild = message.guild
		if not (await self.check_log('deletes', guild)):
			return
		if not self.other_checks(message):
			return
		author = message.author
		desc = f'<@{author.id}> deleted their message.'
		fields = [('**Message Content**', message.content)]
		timestamp = datetime.now()
		await log(
			message,
			desc,
			timestamp,
			'**Message delete**',
			0xde8e16,
			fields=fields,
			showauth=True
		)

	@commands.Cog.listener()
	async def on_bulk_message_delete(self, messages):
		guild = messages[0].guild
		print(len(messages))
		if not (await self.check_log('bulkdelete', guild)):
			print('False?')
			return

		desc = 'Multiple messages were deleted.'
		users = {}
		field_desc = ''
		for message in messages:
			if message.author in users:
				users[message.author] += 1
			else:
				users[message.author] = 1
		for user in users:
			field_desc += '''
\n\n{0} of <@{1.id} ({1.name}{1.discriminator}\'s messages were deleted)
			'''.format(users[user], user)
		await log(
			messages[0],
			desc,
			'**Messages Deleted**',
			0xff2a00,
			fields=[('**Deleted Messages**', field_desc)]
		)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.bot:
			return
		guild = member.guild
		if not (await self.check_log('joins', guild)):
			return
		timestamp = datetime.now()
		desc = f'<@{member.id}> has joined the server!'
		await log(
			None,
			desc,
			timestamp,
			'**Member Join**',
			0xe6e609,
			show_user=member,
			no_msg=guild
		)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		if member.bot:
			return
		guild = member.guild

		ban_logs = guild.audit_logs(
			limit=2,
			action=AuditLogAction.ban
		)
		kick_logs = guild.audit_logs(
			limit=3,
			action=AuditLogAction.kick
		)

		fields = [('**User Id**', member.id, True)]

		async for audit_log in kick_logs:
			if audit_log.target == member:

				await self.handle_kick(member, audit_log)
				return

		async for audit_log in ban_logs:
			if audit_log.target == member:
				return

		if not (await self.check_log('joins', guild)):
			return
		timestamp = datetime.now()
		desc = f'<@{member.id}> has left the server.'
		roles = member.roles
		print(roles)
		str_roles = ', '.join(
			[f'<@&{role.id}>' for role in roles if role.name != '@everyone']
		)

		if str_roles == '':
			str_roles = 'None'

		fields = [('**Roles**', str_roles)]

		await log(
			None,
			desc,
			timestamp,
			'**Member Leave**',
			0xe6e609,
			show_user=member,
			no_msg=guild,
			fields=fields
		)

	@commands.Cog.listener()
	async def on_member_ban(self, guild, member):
		0xff1900
		if member.id == 527937324865290260:  # I ban my alt a lot.
			await guild.unban(member)
		relevant_logs = guild.audit_logs(
			limit=5,
			action=AuditLogAction.ban
		)
		user = None
		fields = [('**User Id**', member.id, True)]
		async for audit_log in relevant_logs:
			if audit_log.target == member:

				user = audit_log.user
				if user == self.bot.user:
					return
				timestamp = audit_log.created_at
				reason = audit_log.reason
				if reason is None:
					reason = "No reason provided."
				print(user, timestamp, reason)
				break
		if user is None:
			desc = f'<@{member.id}> was banned from the server.'
			timestamp = datetime.now()
		elif user == self.bot.user:
			return
		else:
			desc = f'<@{user.id}> banned <@{member.id}>.'

			fields.append(('**Reason**', reason, True))
		await log(
			None,
			desc,
			timestamp,
			'**Member Ban**',
			0xff1900,
			show_user=member,
			no_msg=guild,
			fields=fields
		)

	async def handle_kick(self, member, audit_log):
		fields = []
		guild = member.guild
		user = audit_log.user
		reason = audit_log.reason
		timestamp = audit_log.created_at
		if user == self.bot.user:
			return
		else:
			desc = f'<@{user.id}> kicked <@{member.id}>.'
			if reason is not None:
				fields.append(('**Reason**', reason, True))
			else:
				fields.append(('**Reason**', 'None provided.', True))
		await log(
			None,
			desc,
			timestamp,
			'**Member Kick**',
			0xff1900,
			show_user=member,
			no_msg=guild,
			fields=fields
		)

def setup(bot):
	bot.add_cog(Logger(bot))
