import asyncio
import discord
import datetime
from rw import read, write
from checkTrust import checkTrust
from role_find import get_muted_role
helpMsg = discord.Embed(title='Customization', description='''
**`ban <user> <time*> <reason*>`:**  Ban a user for a period of time.

**`kick <user> <reason*>`:**  Kick a user.

**`mute <user> <time*> <reason*>`:**  Mute a user for a period of time.

**`unmute <user> <reason*>`:**  Unmute a user.

**`banword <phrase>`:**  Ban a string.

**`unbanword <phrase>`:**  Unban a string.

**`banreaction <emoji>`:**  Ban a reaction.

**`unbanreaction <emoji>`:**  Unban a reaction.

**`banlist`:**  Get a list of all banned reactions and strings.

**`warn <user> <reason>`:**  Warn a user.

(*=optional)
''', color=0xd82222)


async def log(text, msg, title='Moderation', footer=''):
	guild = msg.guild
	log_embed = discord.Embed(
		title=title,
		description=text,
		color=0xd82222
	)
	log_embed.set_footer(text=footer)
	log_dict = await read('al')
	action_log_id = log_dict[guild.id]
	log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
	await log_channel.send(embed=log_embed)


def findDate(string):

	now = datetime.datetime.now()
	strNow = datetime.datetime.now().strftime("%Y-%m-%w-%W %H:%M:%S")
	timeTypes = [
		'd',
		'm',
		'w',
		's',
		'h',
		'mo'
	]

	date = strNow.split(' ')[0].split('-')
	time = strNow.split(' ')[1].split(':')

	if string[-1] == '':
		date[1] = str(int(date[1]) + int(string[:-1]))

	elif string[-1] == 'd':
		date[2] = str(int(date[2]) + int(string[:-1]))

	elif string[-1] == 'w':
		date[3] = str(int(date[3]) + int(string[:-1]))

	elif string[-1] == 's':
		time[2] = str(now.second + int(string[:-1]))

	elif string[-1] == 'm':
		time[1] = str(now.minute + int(string[:-1]))

	elif string[-1] == 'h':
		time[0] = str(now.hour + int(string[:-1]))
	# print(date, time)
	if string[-1] in timeTypes:

		try:
			while int(time[2]) > 59:
				time[2] = str(int(time[2]) - 60)
				time[1] = str(int(time[1]) + 1)

			while int(time[1]) > 59:
				time[1] = str(int(time[1]) - 60)
				time[0] = str(int(time[0]) + 1)
				# print(time[1])
			while int(time[0]) > 23:
				time[0] = str(int(time[0]) - 24)
				date[2] = str(int(date[2]) + 1)
			while int(date[2]) > 6:
				date[2] = str(int(date[2]) - 6)
				date[3] = str(int(date[3]) + 1)
			while int(date[3]) > 51:
				date[3] = str(int(date[3]) - 51)
				date[0] = str(int(date[0]) + 1)
			while int(date[1]) > 11:
				date[1] = str(int(date[1]) - 11)
				date[0] = str(int(date[0]) + 1)
			# print(date, time)
			for a in range(len(time)):
				# print(time[a])
				if len(time[a]) == 1:
					time[a] = '0' + str(a)
			for a in date:
				if len(a) == 1:
					a = '0' + a
			newDate = '-'.join(date) + ' ' + ':'.join(time)
			return str(newDate)
		except ValueError:
			pass

	else:
		try:
			newDate = now.day + int(string)

			return newDate
		except:
			return False


async def ban(args, msg):
	try:
		args.remove('')
	except ValueError:
		pass
	if msg.author.guild_permissions.administrator:

		channel = msg.channel
		guild = msg.guild
		if len(args) > 1:
			try:
				date = findDate(args[1])
				if date != False:
					date_found = True
				else:
					date_found = False
			except IndexError:
				date_found = False
		else:
			date_found = False
		banUserId = msg.mentions[0].id
		if date_found:
			bl = (await read('banList'))
			if guild.id not in bl:
				bl[guild.id] = {}
			bl[guild.id][banUserId] = str(date)
			await write('banList', bl)
			if len(args) > 2:
				reason = ' '.join(args[2:])
				user = guild.get_member(banUserId)
				username = user.display_name
				await guild.ban(user=user, reason=reason)
				await channel.send('User has been banned')
				log_dict = await read('al')
				if guild.id in log_dict:

					disp_name = msg.author.display_name
					await log(
						f'@{disp_name} banned @{username} for **reason:** `{reason}`  **duration:** `{args[1]}`',
						msg
					)
				else:
					print('oof')

			else:
				username = guild.get_member(banUserId).display_name
				await guild.ban(user=guild.get_member(banUserId))
				await channel.send('User has been banned')
				log_dict = await read('al')
				if guild.id in log_dict:

					disp_name = msg.author.display_name
					await log(
						f'@{disp_name} banned @{username} for  `{args[1]}`',
						msg
					)
		else:
			if len(args) > 1:
				reason = ' '.join(args[1:])
				username = guild.get_member(banUserId).display_name
				await guild.ban(user=guild.get_member(banUserId), reason=reason)
				await channel.send('User has been banned')
				log_dict = await read('al')
				if guild.id in log_dict:

					disp_name = msg.author.display_name
					await log(
						f'@{disp_name} banned @{username} for **reason:** `{reason}`',
						msg
					)
			else:
				username = guild.get_member(banUserId).display_name
				await guild.ban(user=guild.get_member(banUserId))
				message = await channel.send('User has been banned')
				log_dict = await read('al')
				if guild.id in log_dict:
					disp_name = msg.author.display_name
					await log(
						f'@{disp_name} banned @{username}',
						msg
					)
				await asyncio.sleep(5)
				await message.delete()

	else:
		await msg.channel.send('You do not have permission to use this command')


async def unban(args, msg):
	try:
		args = args.remove(' ')
	except ValueError:
		pass
	if msg.author.guild_permissions.administrator:
		channel = msg.channel
		guild = msg.guild
		dispName = msg.author.display_name
		banLogs = await guild.bans()
		banIds = [y.user.id for y in banLogs]
		userId = int(args[0])
		banEntry = await guild.bans()
		if userId not in banIds:
			await channel.send('User is not banned!')

		else:
			for each in banEntry:
				if each.user.id == userId:
					user = each.user
					break
			log_dict = await read('al')
			if guild.id in log_dict:
				log_action = True
			else:
				log_action = False

			ban_list = await read('banList')
			if guild.id in ban_list:
				guild_ban_list = ban_list[guild.id]
				if user.id in guild_ban_list:
					del ban_list[guild.id][user.id]
			if len(args) > 1:
				print(args)
				reason = ' '.join(args[1:])
				await guild.unban(user=user, reason=reason)
				await channel.send('User has been unbanned')
				if log_action:
					disp_name = msg.author.display_name
					username = user.display_name
					await log(
						f'@{disp_name} unbanned @{username} for **reason:** `{reason}`',
						msg
					)
			else:
				await channel.send('User has been unbanned')
				await guild.unban(user=user, reason=dispName + ' unbanned them.')
				if log_action:
					disp_name = msg.author.display_name
					username = user.display_name
					await log(
						f'@{disp_name} unbanned @{username}',
						msg
					)

		print('unbanning')

	else:
		await msg.channel.send('You do not have permission to use this command')


async def kick(args, msg):
	author = msg.author
	guild = msg.guild
	trusted = await checkTrust(guild, author)
	channel = msg.channel
	print(trusted)
	if msg.author.guild_permissions.administrator or trusted:
		mentions = msg.mentions
		username = msg.author.display_name
		kickname = mentions[0].display_name
		if len(mentions) == 1:
			if len(args) == 1:

				disp_name = author.display_name
				await log(f'@{disp_name} kicked @{kickname}')
				await msg.guild.kick(mentions[0], reason=f'@{username} kicked them.')
			else:
				args[1] = args[1:]

				disp_name = author.display_name
				await log(f'@{disp_name} kicked @{kickname} for **reason:** `{args[1]}')
				await guild.kick(mentions[0], reason=args[1])
			await channel.send(f'{kickname} has been kicked')

		else:
			await channel.send(
				'Invalid ammount of args. Example command: `kick @jon#2342 lol`'
			)
	else:
		await channel.send('You do not have the permission to use this command')


async def mute(args, msg):

	author = msg.author
	guild = msg.guild
	trusted = await checkTrust(guild, author)
	guild = msg.guild
	muted_role = await get_muted_role(guild)
	try:
		args.remove('')
	except ValueError:
		pass
	if author.guild_permissions.administrator or trusted:
		channel = msg.channel
		guild = msg.guild
		if len(args) > 1:
			try:
				date = findDate(args[1])
				if date is not False:
					date_found = True
				else:
					date_found = False
			except IndexError:
				date_found = False
		else:
			date_found = False
		mute_user_id = msg.mentions[0].id
		if date_found:
			user = guild.get_member(mute_user_id)
			muteList = await read('muteList')
			if guild.id in muteList:
				guild_muteList = muteList[guild.id]
			else:
				guild_muteList = {}
			if user.id in guild_muteList:

				guild_muteList[user.id]['timeup'] = date

			else:
				guild_muteList[user.id] = {'Offenses': 0, 'timeup': date}

			muteList[guild.id] = guild_muteList
			await write('muteList', muteList)

			if len(args) > 2:
				reason = ' '.join(args[2:])
				user = guild.get_member(mute_user_id)

				await user.add_roles(muted_role, reason=reason)

				await channel.send('User has been muted')
				log_dict = await read('al')
				if guild.id in log_dict:

					await log(
						f'<@{author.id}> muted <@{user.id}> for **reason:** `{reason}`  **duration:** `{args[1]}`',
						msg
					)
				else:
					print('oof')

			else:
				print('no oof')
				user = guild.get_member(mute_user_id)
				username = user.display_name
				await user.add_roles(muted_role)
				await channel.send('User has been muted')
				log_dict = await read('al')
				if guild.id in log_dict:
					disp_name = msg.author.display_name
					await log(
						f'`{disp_name}` muted {username} for  `{args[1]}`',
						msg
					)
		else:
			if len(args) > 1:
				reason = ' '.join(args[1:])
				username = guild.get_member(mute_user_id).display_name
				user = msg.mentions[0]
				await user.add_roles(muted_role, reason=reason)
				await channel.send('User has been muted')
				log_dict = await read('al')
				if guild.id in log_dict:
					disp_name = msg.author.display_name
					await log(
						f'`{disp_name}` muted {username} for **reason:** `{reason}`',
						msg
					)
				perma_list = await read('permaMute')
				if guild.id in perma_list:
					guild_perma_list = perma_list[guild.id]
				else:
					guild_perma_list = []
				guild_perma_list.append(user.id)
				perma_list[guild.id] = guild_perma_list
				await write('permaMute', perma_list)
			else:
				user = guild.get_member(mute_user_id)
				username = user.display_name
				await user.add_roles(muted_role)
				message = await channel.send('User has been muted')
				log_dict = await read('al')
				if guild.id in log_dict:
					disp_name = msg.author.display_name
					await log(
						f'`{disp_name}` muted {username}',
						msg
					)
				perma_list = await read('permaMute')
				if guild.id in perma_list:
					guild_perma_list = perma_list[guild.id]
				else:
					guild_perma_list = []
				guild_perma_list.append(user.id)
				perma_list[guild.id] = guild_perma_list
				await write('permaMute', perma_list)
				await asyncio.sleep(5)
				await message.delete()

	else:
		await msg.channel.send('You do not have permission to use this command')


async def unmute(args, msg):

	author = msg.author
	guild = msg.guild
	trusted = await checkTrust(guild, author)
	guild = msg.guild
	muted_role = await get_muted_role(guild)
	log_dict = await read('al')
	if guild.id in log_dict:

		disp_name = msg.author.display_name
	else:
		log_actions = False
	try:
		args.remove('')
	except ValueError:
		pass
	user = msg.mentions[0]
	username = user.display_name
	if author.guild_permissions.administrator or trusted:
		channel = msg.channel
		guild = msg.guild
		if len(args) > 1:
			reason = ' '.join(args[1:])
			print(reason)
			await user.remove_roles(muted_role, reason=reason)
			await log(
				f'`{disp_name}` unmuted {username}, for **reason:** {reason}',
				msg
			)
		else:
			await user.remove_roles(muted_role)
			await log(
				f'`{disp_name}` unmuted {username}',
				msg
			)
		'''mute_list = await read('muteList')
		if guild.id in mute_list:
			guild_mute_list = mute_list[guild.id]
			if user.id in guild_mute_list:
				del mute_list[guild.id][user.id]
				await write('muteList', mute_list)'''
		perma_list = await read('permaMute')
		if guild.id in perma_list:
			guild_perma_list = perma_list[guild.id]
			print(perma_list)
			if user.id in guild_perma_list:
				perma_list[guild.id].remove(user.id)
				await write('permaMute', perma_list)

	else:
		await msg.channel.send('You do not have permission to use this command')


async def warn(args, msg):
	guild = msg.guild
	author = msg.author
	channel = msg.channel
	trusted = await checkTrust(guild, author)
	if author.guild_permissions.administrator or trusted:
		if len(args) > 1:
			if len(msg.mentions) >= 1:
				user = msg.mentions[0]
			else:
				try:
					user = guild.get_member(int(args[0]))
				except ValueError:
					user = guild.get_member_named(args[0])

			reason = ' '.join(args[1:])
			dm_channel = await user.create_dm()
			await dm_channel.send(
				f'You have been warned on {guild.name} for **reason:** {reason}'
			)

			warn_dict = await read('warn_list')
			if guild.id in warn_dict:
				guild_warn_dict = warn_dict[guild.id]
			else:
				guild_warn_dict = {'instances': 0, 'cases': {}}
			date = datetime.datetime.now()
			date_str = date.strftime("%m-%d-%Y")
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
			await log(
				f'<@{author.id}> warned <@{user.id}> for **reason**:  `{reason}`',
				msg,
				'Warn',
				f'{date_str} | Case #{warn_id}'
			)

		elif len(args) == 1:
			await channel.send('You need to have a reason to warn someone!')
		else:
			await channel.send(
				'Invalid arg ammount. Example command: `?warn jonnyboy dont do that!`'
			)
	else:
		await channel.send('You do not have permission to do that!')


async def get_warns(args, msg):
	guild = msg.guild
	author = msg.author
	channel = msg.channel
	trusted = await checkTrust(guild, author)
	if trusted or author.guild_permissions.administrator:
		warn_dict = await read('warn_list')

		if guild.id in warn_dict:
			guild_warn_dict = warn_dict[guild.id]
			if len(msg.mentions) >= 1:
				user = msg.mentions[0]

			else:
				try:
					user = guild.get_member(int(args[0]))
				except ValueError:
					user = guild.get_member_named(args[0])
			if user != "NoneType":
				if user.id in guild_warn_dict:
					user_warns = guild_warn_dict[user.id]

					embed = discord.Embed(title=f'{user.display_name}', color=0xfffc00)
					embed.add_field(name=f'Warnings:', value='\u200B', inline=False)
					for a in user_warns:
						warn = user_warns[a]
						reason = warn['reason']
						date = warn['date']
						moderator = warn['moderator']
						embed.add_field(

							name=f'Case: {a}',
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
					await channel.send(embed=embed)
				else:
					await channel.send('User has no warns!')
			else:
				await channel.send("Invalid user")
		else:
			await channel.send('Your server has no warns yet!')
	else:
		await channel.send('You do not have permission to use this command!')
	pass  # O wait i have to make warns make a dictionary first


async def remove_warn(args, msg, client):
	guild = msg.guild
	author = msg.author
	channel = msg.channel
	while '' in args:
		args.remove('')
	if author.guild_permissions.administrator:
		warn_dict = await read('warn_list')
		if guild.id in warn_dict:
			guild_warn_dict = warn_dict[guild.id]
			try:
				case_number = int(args[0])
				cases = guild_warn_dict['cases']

				if case_number in cases:
					path = cases[case_number]
					path = path.split('/')
					print(path)
					user = guild.get_member(int(path[0]))
					embed = discord.Embed(title=f'{user.display_name}', color=0xfffc00)
					embed.add_field(name=f'Warning:', value='\u200B', inline=False)

					warn = guild_warn_dict[int(path[0])][int(path[1])]
					reason = warn['reason']
					date = warn['date']
					moderator = warn['moderator']
					embed.add_field(

						name=f'Case: {path[1]}',
						value=reason,
						inline=True
					)
					embed.add_field(
						name=date,
						value=f'Warned by: <@{moderator}>',
						inline=True
					)
					embed.set_footer(text='This message has a 10s timeout.')
					check_msg = await channel.send(
						'Are you sure that you would like to remove this warning? You cannot undo this!:'
						, embed=embed)
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
						return user == author and good_emoji and reaction.message.id == check_msg.id

					try:
						reaction, user = await client.wait_for(
							'reaction_add',
							timeout=10.0,
							check=check
						)

					except asyncio.TimeoutError:
						await channel.send('Message timed out.')
					else:
						if user_reply == '✅':

							del warn_dict[guild.id][int(path[0])][int(path[1])]
							await write('warn_list', warn_dict)
							await channel.send('Warning has been deleted.')
						else:
							await channel.send('Warning will not be deleted.')
				else:
					await channel.send('That instance doesn\'t exist!')
			except ValueError:
				await channel.send(f'{args[0]} is not a valid number!')
		else:
			await channel.send('There are no warnings in your guild!')
