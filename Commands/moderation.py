import discord
import asyncio
from datetime import datetime
from discord.ext import commands
from utils import get_muted_role
from tools.read_write import read, write
from utils import find_date, InvalidDate


class Moderation(commands.Cog, name='Moderation'):
	'''Moderation Commands'''

	def __init__(self, bot):
		self.bot = bot
		self.color = 0xd91111

	def cog_check(self, ctx):
		author = ctx.author
		if author.guild_permissions.administrator:
			return True
		else:
			return False

			# cmd_name = ctx.command.name
			# return check_trust(cmd_name, author)

	async def log(
		self,
		ctx,
		desc,
		title='**Moderation**',
		color=0xff0000,
		**kwargs
	):

		guild = ctx.guild
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
		now = datetime.now()
		log_embed.timestamp = now
		log_dict = await read('al')
		action_log_id = log_dict[guild.id]
		log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
		await log_channel.send(embed=log_embed)

	@commands.command(name='banword', aliases=['bw'])
	async def ban_word(self, ctx, *_):
		'''Bans a phrase from user messages.
		```css
		example usage:
		``````py
		?banword badword  # Bans "badword from messages"
		``````py
		?bw bad word  # Bans "bad word" from messages'''
		msg = ctx.message
		guild = ctx.guild
		author = ctx.author
		phrase = msg.content.split(None, 1)[1]
		lower_phrase = phrase.lower()
		fd = await read('banWords', True, False)

		if guild.id in fd:
			guild_list = fd[guild.id]

		else:
			guild_list = []

		if lower_phrase not in guild_list:
			guild_list.append(lower_phrase)
			failed = False

		else:
			await ctx.send(
				f"`{phrase}` is already in the server's ban list!"
			)
			failed = True

		if not failed:
			fd[guild.id] = guild_list
			await write('banWords', fd, False)
			await self.log(
				ctx,
				f"<@{author.id}> added `{phrase}` to the server's ban list.",
				'**Banword**',
				showauth=True
			)
			await ctx.send(f"`{phrase}` has been added to the server's ban list.")

	@commands.command(name='unbanword', aliases=['unbw'])
	async def unban_word(self, ctx, *_):
		'''Unbans a string or word from user messages.
		```css
		example usage:
		``````fix
		unbanword allseeingbot
		``````fix
		unbw all seeing bot'''
		msg = ctx.message
		guild = ctx.guild
		author = ctx.author
		phrase = msg.content.split(None, 1)[1]
		lower_phrase = phrase.lower()
		fd = await read('banWords', True, False)

		if guild.id in fd:
			guild_list = fd[guild.id]

		else:
			guild_list = []

		if lower_phrase in guild_list:
			guild_list.remove(lower_phrase)
			failed = False

		else:
			await ctx.send(
				f"`{phrase}` is not in the server's ban list!"
			)
			failed = True

		if not failed:
			fd[guild.id] = guild_list
			await write('banWords', fd, False)
			await self.log(
				ctx,
				f"<@{author.id}> removed `{phrase}` from the server's ban list.",
				'**Banword**',
				showauth=True
			)
			await ctx.send(f"`{phrase}` has been removed from the server's ban list.")

	@commands.command(name='banreaction', aliases=['br'])
	async def ban_reaction(self, ctx, *_):
		'''Bans a reaction.
		```css
		Example Usage:
		``````css
		?banreaction ✅ //Bans the reaction ✅
		```'''
		msg = ctx.message
		guild = ctx.guild
		author = ctx.author
		phrase = msg.content.split(None, 1)[1]
		lower_phrase = phrase.lower()
		fd = await read('banEmojis', True, False)

		if guild.id in fd:
			guild_list = fd[guild.id]

		else:
			guild_list = []

		if lower_phrase not in guild_list:
			guild_list.append(lower_phrase)
			failed = False

		else:
			await ctx.send(
				f"`{phrase}` is already in the server's ban list!"
			)
			failed = True

		if not failed:
			fd[guild.id] = guild_list
			await write('banEmojis', fd, False)
			await self.log(
				ctx,
				f"<@{author.id}> added `{phrase}` to the server's ban list.",
				'**Ban reaction**',
				showauth=True
			)
			await ctx.send(f"`{phrase}` has been added to the server's ban list.")

	@commands.command(name='unbanreaction', aliases=['unbr'])
	async def unban_reaction(self, ctx, *_):
		'''Unbans a reaction.
		```css
		Example Usage:
		``````css
		?unbanreaction ✅ // Allows users to react to messages with the ✅ emoji again
		```'''
		msg = ctx.message
		guild = ctx.guild
		author = ctx.author
		phrase = msg.content.split(None, 1)[1]
		lower_phrase = phrase.lower()
		fd = await read('banEmojis', True, False)

		if guild.id in fd:
			guild_list = fd[guild.id]

		else:
			guild_list = []

		if lower_phrase in guild_list:
			guild_list.remove(lower_phrase)
			failed = False

		else:
			await ctx.send(
				f"`{phrase}` is not in the server's ban list!"
			)
			failed = True

		if not failed:
			fd[guild.id] = guild_list
			await write('banEmojis', fd, False)
			await self.log(
				ctx,
				f"<@{author.id}> removed `{phrase}` from the server's ban list.",
				'**Banreaction**',
				showauth=True
			)
			await ctx.send(f"`{phrase}` has been removed from the server's ban list.")

	@commands.command(name='banlist')
	async def list_banned_content(self, ctx):
		'''Get a list of banned words and reactions in the server.
		```css
		Example Usage:
		``````css
		?banlist // Get a list of all banned words and reactions in the server.
		```'''
		guild = ctx.guild
		fd = await read('banWords', True, False)
		if guild.id not in fd:
			fd[guild.id] = []
			await write('banWords', fd, False)
		ban_words = fd[guild.id]
		fd = await read('banEmojis', True, False)
		if guild.id not in fd:
			fd[guild.id] = []
			await write('banEmojis', fd, False)
		ban_emojis = fd[guild.id]
		embed = discord.Embed(
			title='**Banned Content:**',
			color=0xeb5e34
		)
		if ban_words is not []:
			ban_word_content = '```css\n'
			for a in range(len(ban_words)):
				ban_word_content += f'{a+1}: {ban_words[a]}\n'
			ban_word_content += '```'
		else:
			ban_word_content = 'None'
		if ban_emojis is not []:
			ban_emoji_content = '```css\n'
			for a in range(len(ban_emojis)):
				ban_emoji_content += f'{a+1}: {ban_emojis[a]}\n'

			ban_emoji_content += '```'
		else:
			ban_emoji_content = 'None'
		embed.add_field(
			name='**Banned Words:**',
			value=ban_word_content,
			inline=True
		)
		embed.add_field(
			name='**Banned Reactions:**',
			value=ban_emoji_content,
			inline=True
		)
		print(ban_emoji_content)
		await ctx.send(embed=embed)

	@commands.command(name='kick', aliases=['k'])
	async def kick(self, ctx, user: discord.Member, *_):
		'''Kick a user.
		```css
		Example Usage:```
		```css
		?kick <user> bc i can // Kicks <user> for bc i can```'''
		msg = ctx.message
		author = ctx.author
		try:
			reason = msg.content.split(None, 1)[1]
			found_reason = True
		except IndexError:
			found_reason = False
		if found_reason:
			await self.log(
				ctx,
				f'<@{author.id} kicked <@{user.id}>',
				fields=[
					('**Reason:**', reason)
				]
			)
		else:
			await self.log(
				ctx,
				f'<@{author.id} kicked <@{user.id}>'
			)

	@commands.command(name='ban')
	async def ban(self, ctx, user: discord.Member, time=None, *argv):
		'''Ban a user.
		```css
		Example Usage:
		```
		```css
		?ban <user> bc i can// Bans <user> from the guild for the reason bc i can
		``````css
		?ban <user> 5d bc i can // Bans <user> for 5 days with the reason bc i can'''
		fields = []
		guild = ctx.guild
		if time is not None:
			try:
				duration = find_date(time)
				end_date = duration + datetime.now()

				end_date.strftime('%Y-%m-%w-%W %H:%M:%S')
				ban_list = await read('banList')
				if guild.id in ban_list:
					guild_list = ban_list[guild.id]
				else:
					guild_list = {}
				guild_list[user.id] = end_date
				ban_list[guild.id] = guild_list
				await write('banList', ban_list)
				fields.append(
					('**Duration:**', f'`{time}`', True)
				)
			except InvalidDate:
				argv = list(argv)
				argv.insert(0, time)

		author = ctx.author
		if len(argv) > 0:
			reason = ' '.join(argv)
			fields.append(
				('**Reason:**', reason, True)
			)

		await self.log(
			ctx,
			f'<@{author.id}> banned <@{user.id}>',
			fields=fields,
			showauth=True
		)
		embed = discord.Embed(
			title='**Ban**',
			description=f'<@{user.id}> has been banned.',
			color=0xff0000
		)
		await ctx.send(embed=embed)

	@commands.command(name='unban', aliases=['pardon'])
	async def unban(self, ctx, user: discord.User, *argv):
		'''Unban a user from the guild.
		```css
		Example Usage:
		``````css
		?unban <user id> i didnt mean to ban them // Unbans the user with the id <user id> from the guild
		```'''
		fields = []
		guild = ctx.guild

		ban_list = await read('banList')
		if guild.id in ban_list:
			if user.id in ban_list:
				del ban_list[guild.id][user.id]
				await write('banList', ban_list)

		author = ctx.author
		try:
			reason = ' '.join(argv)
			fields.append(
				('**Reason:**', reason, True)
			)
		except IndexError:
			pass

		await self.log(
			ctx,
			f'<@{author.id}> unbanned <@{user.id}>',
			fields=fields,
			showauth=True
		)

	@commands.command(name='mute', aliases=['silence'])
	async def mute(self, ctx, user: discord.Member, time=None, *argv):
		'''Mute a user so that they cannot send messages anymore.
		```css
		Example Usage:
		``````css
		?mute <user> 5d bc i can // Mutes <user> for 5 days with the reason because i can.
		``````css
		?mute <user> bc i can // Mutes <user> permanately for reason bc i can
		```'''

		fields = []
		guild = ctx.guild
		if time is not None:
			try:
				duration = find_date(time)
				end_date = duration + datetime.now()

				end_date.strftime('%Y-%m-%w-%W %H:%M:%S')
				mute_list = await read('muteList')
				if guild.id in mute_list:
					guild_list = mute_list[guild.id]
				else:
					guild_list = {}
				guild_list[user.id] = end_date
				mute_list[guild.id] = guild_list
				await write('muteList', mute_list)
				fields.append(
					('**Duration:**', f'`{time}`', True)
				)
			except InvalidDate:
				argv = list(argv)
				argv.insert(0, time)

		author = ctx.author
		if len(argv) > 0:
			reason = ' '.join(argv)
			fields.append(
				('**Reason:**', reason, True)
			)

		await self.log(
			ctx,
			f'<@{author.id}> muted <@{user.id}>',
			fields=fields,
			showauth=True
		)
		muted_role = await get_muted_role(guild)
		await user.add_roles(muted_role)
		embed = discord.Embed(
			title='**Mute**',
			description=f'<@{user.id}> has been muted.',
			color=0xff0000
		)
		await ctx.send(embed=embed)

	@commands.command(name='unmute')
	async def unmute(self, ctx, user: discord.Member, *argv):
		'''Unmute a user.
		```css
		Example usage:
		``````css
		?unmute <user> oops wrong person // Unbans <user> for the reason oops wrong person.
		```'''
		fields = []
		guild = ctx.guild

		mute_list = await read('muteList')
		if guild.id in mute_list:
			if user.id in mute_list:
				del mute_list[guild.id][user.id]
				await write('muteList', mute_list)

		author = ctx.author
		try:
			reason = ' '.join(argv)
			fields.append(
				('**Reason:**', reason, True)
			)
		except IndexError:
			pass

		await self.log(
			ctx,
			f'<@{author.id}> unmuted <@{user.id}>',
			fields=fields,
			showauth=True
		)
		muted_role = await get_muted_role(guild)
		await user.remove_roles(muted_role)

	@commands.command(name='warn', aliases=['hint', 'suggest'])
	async def warn(self, ctx, user: discord.Member, *argv):
		'''Warn a user.
		```css
		Example Usage:
		``````css
		?warn <user> dont say that word // Warns <user> dont say that word.```'''
		guild = ctx.guild
		author = ctx.author
		warn_dict = await read('warn_list')
		reason = ' '.join(argv)
		if guild.id in warn_dict:
			guild_warn_dict = warn_dict[guild.id]

		else:
			guild_warn_dict = {'instances': 0, 'cases': {}}

		date = datetime.now()
		date_str = date.strftime('%Y-%m-%w-%W %H:%M:%S')
		if user.id in guild_warn_dict:
			user_warns = guild_warn_dict[user.id]
		else:
			user_warns = {}
		warn_id = guild_warn_dict['instances'] + 1
		warn_info = {
			'moderator': author.id,
			'reason': reason,
			'date': date_str
		}
		user_warns[warn_id] = warn_info
		guild_warn_dict[user.id] = user_warns
		guild_warn_dict['instances'] += 1
		cases = guild_warn_dict['cases']
		cases[warn_id] = f'{user.id}/{warn_id}'
		guild_warn_dict['cases'] = cases
		warn_dict[guild.id] = guild_warn_dict
		print(warn_dict)
		await write('warn_list', warn_dict)
		warn_embed = discord.Embed(
			title='**Warned**',
			description=f'You have been warned on `{guild.name}`.',
			color=0xff0000
		)
		warn_embed.add_field(
			name='**Warning:**',
			value=reason
		)
		await user.send(embed=warn_embed)

		await self.log(
			ctx,
			f'<@{author.id}> warned <@{user.id}>.',
			title='**Warn**',
			fields=[('**Warn Content:**', reason)],
			showauth=True
		)
		embed = discord.Embed(
			title='**Warn**',
			description=f'Warned <@{user.id}>.',
			color=0xff0000
		)
		await ctx.send(embed=embed)

	@commands.command(name='warns', aliases=['warnlist', 'listwarns'])
	async def get_warns(self, ctx, user: discord.Member):
		'''List a user's warns.
		```css
		Example Usage:
		``````css
		?listwarns <user> // Get a list of <user>'s warns'''
		print(user.id)
		guild = ctx.guild
		full_warn_dict = await read('warn_list')
		if guild.id in full_warn_dict:
			guild_warn_dict = full_warn_dict[guild.id]
		else:
			guild_warn_dict = {}
		if user.id in guild_warn_dict:
			user_warns = guild_warn_dict[user.id]
			print('a')
			embed = discord.Embed(
				color=0xfffc00
			)

			name = user.display_name
			icon_url = user.avatar_url
			embed.set_author(
				name=name,
				icon_url=icon_url
			)
			for a in user_warns:
				warn = user_warns[a]
				reason = warn['reason']
				date = warn['date']

				date = date.replace('-', '/', 2)
				date = date.split('-')[0]
				moderator = warn['moderator']
				embed.add_field(

					name=f'**Instance {a}:**',
					value=reason,
					inline=True
				)
				embed.add_field(
					name=date,
					value=f'warned by: <@{moderator}>',
					inline=True
				)
				embed.add_field(name='\u200B', value='\u200B', inline=False)
			embed.remove_field(-1)
			await ctx.send(embed=embed)
		else:
			await ctx.send('User has no warns!')

	@commands.command(name='removewarn', aliases=['rm'])
	async def pardon_warn(self, ctx, instance: int, *argv):
		'''Remove a users warn.
		```css
		Example Usage:
		``````css
		?removewarn <case number> // Remove the warning represented by <case number> '''
		warn_dict = await read('warn_list')
		guild = ctx.guild
		if guild.id in warn_dict:
			guild_warn_dict = warn_dict[guild.id]
			cases = guild_warn_dict['cases']
		else:
			cases = {}
		bot = self.bot
		author = ctx.author
		if instance in cases:
				path = cases[instance]
				path = path.split('/')
				print(path)
				user = guild.get_member(int(path[0]))
				embed = discord.Embed(color=0xfffc00)
				name = user.display_name
				icon_url = user.avatar_url
				embed.set_author(
					name=name,
					icon_url=icon_url
				)
				embed.add_field(name=f'Warn content:', value='\u200B', inline=False)

				warn = guild_warn_dict[int(path[0])][int(path[1])]
				reason = warn['reason']
				date = warn['date']

				date = date.replace('-', '/', 2)
				date = date.split('-')[0]
				moderator = warn['moderator']
				embed.add_field(

					name=f'**Instance: {path[1]}**',
					value=reason,
					inline=True
				)
				embed.add_field(
					name=date,
					value=f'Warned by: <@{moderator}>',
					inline=True
				)
				embed.set_footer(text='This message has a 10s timeout.')
				check_msg = await ctx.send(
					'Are you sure that you would like to remove this warning? '
					'This cannot be undone.',
					embed=embed)
				await check_msg.add_reaction('✅')
				await check_msg.add_reaction('❌')

				def check(reaction, user):
					global user_reply
					print(str(reaction.emoji))
					if str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌':
						good_emoji = True
						user_reply = str(reaction.emoji)
					else:
						good_emoji = False
					other = reaction.message.id == check_msg.id
					return user == author and good_emoji and other

				try:
					reaction, user = await bot.wait_for(
						'reaction_add',
						timeout=10.0,
						check=check
					)

				except asyncio.TimeoutError:
					await ctx.send('Message timed out.')
				else:
					if user_reply == '✅':

						del warn_dict[guild.id][int(path[0])][int(path[1])]
						await write('warn_list', warn_dict)
						await ctx.send('Warning has been deleted.')
						desc = f"<@{author.id}> removed <@{user.id}>'s warning"
						fields = [
							(f'Warn content:', '\u200B', False),
							(f'**Instance: `{instance}`**', reason, True),
							(f'**{date}**', f'Warned by <@{moderator}>')
						]
						await self.log(
							ctx,
							desc,
							'**Removed Warn**',
							fields=fields,
							showauth=True
						)
					else:
						await ctx.send('Warning will not be deleted.')

	@commands.command(name='purge')
	async def purge(self, ctx, ammount: int, user: discord.Member = None):
		channel = ctx.channel

		def check_user(message):
			return message.author == user
		msg = await ctx.send('Purging messages.')
		if user is not None:
			await channel.purge(
				limit=ammount,
				check=lambda x: x.author == user,
				bulk=True
			)
		else:
			await channel.purge(
				limit=ammount + 1,
				check=lambda x: x != msg,
				bulk=True
			)
		await msg.edit(content='Deleted messages.')
		await asyncio.sleep(2)
		await msg.delete()


def setup(bot):
	bot.add_cog(Moderation(bot))
