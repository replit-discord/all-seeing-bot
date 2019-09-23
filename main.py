import datetime
import discord
import os
import asyncio
import keep_alive
import sys
import ast
from dm_message import mod_mail
from rw import read, write
from cmdDict import cmdDict
from ignoredChars import ignoredChars
from phrase_spam import is_repeating
from encryption_tools import decode
import commands.moderation_tools
from cryptography.fernet import Fernet
from emojiCheck import count as emoji_count
from commands.moderation_tools import findDate
from role_find import get_muted_role
from spam_stuff import log_offense, get_spam_chart, check_expire, spam_chart
# btw most of these imports that are unused are for eval purposes


client = discord.Client()


async def log(text, guild, title='Automatic'):

	log_embed = discord.Embed(
		title=title,
		description=text,
		color=0x00e0f5
	)

	log_dict = await read('al')
	action_log_id = log_dict[guild.id]
	log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
	await log_channel.send(embed=log_embed)
do_setup = True


@client.event
async def on_ready():
	global do_setup
	if do_setup:
		thinger = (await read('test_thinger'))["thinger"][1:]
		b = 0.0
		for a in thinger:
			b += a
		if len(thinger) != 0:
			print(b / len(thinger))
		await write("test_thinger", {"thinger": []})
		await write('bot_prefix', '?')
		bot_prefix = await read('bot_prefix', False)
		game = discord.Game(name='The bot prefix is: ' + bot_prefix)
		await client.change_presence(activity=game)
		print("I'm in")
		print(client.user)
		print('settings up background tasks')
		loop = client.loop
		tasks = loop.create_task(bgTasks())

		await tasks
	do_setup = False


@client.event
async def on_member_join(member):

	guild = member.guild
	log_dict = await read('al')
	action_log_id = log_dict[guild.id]
	log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
	username = member.display_name
	perma_list = await read('permaMute')
	if guild.id in perma_list:
		guild_perma_list = perma_list[guild.id]
		if member.id in guild_perma_list:
			muted_role = await get_muted_role(guild)
			await member.add_roles(
				muted_role,
				reason='User was permanately muted. Role automatically given when they joined.'
			)

			await log_channel.send(
				f'`{username}` was given the mute role because they were muted permanately when they left the server.'
			)

	guild_mute_list = (await read('muteList'))[guild.id]
	if member.id in guild_mute_list:
		muted_role = await get_muted_role(guild)
		await member.add_roles(
			muted_role,
			reason='User\'s mute time is not up yet. They were muted again so they can\'t evade mute.'
		)
		await log_channel.send(
			f'`{username}` was given the mute role because they were muted muted before they left the server, and their duration is not up.'
		)

	print(str(member.display_name) + ' has joined the server!')


@client.event
async def on_message_edit(before, after):
	if after.author != client.user:
		async def log(text, guild, title='Edit'):
			log_embed = discord.Embed(
				title=title,
				description=text,
				color=0x345beb
			)
			log_dict = await read('al')
			action_log_id = log_dict[guild.id]
			log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
			await log_channel.send(embed=log_embed)
		b_content = before.content
		a_content = after.content
		b_content = b_content.replace('`', '')
		a_content = a_content.replace('`', '')
		user = after.author
		await log(
			f'''
	<@{str(user.id)}> edited their message.

	Before:
	`{before.content}`

	After:
	`{after.content}`
	''',
			after.guild
		)


@client.event
async def on_message_delete(message):
	guild = message.guild
	author = message.author
	muted = (await get_muted_role(guild)) in author.roles
	if author != client.user and not muted:
		async def log(text, guild, title='Delete'):
			log_embed = discord.Embed(
				title=title,
				description=text,
				color=0xffa200
			)
			time = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
			log_embed.set_footer(text=time)
			log_dict = await read('al')
			action_log_id = log_dict[guild.id]
			log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
			await log_channel.send(embed=log_embed)
		content = message.content
		content = content.replace('`', '')
		user = message.author
		await log(
			f'''
<@{str(user.id)}>'s message was deleted.

Message:
`{content}`
	''',
			guild
		)


@client.event
async def on_message(message):
	startTime = datetime.datetime.now()

	def mark_time(lable):
		print(lable, datetime.datetime.now() - startTime)

	private = str(message.channel.type) == 'private'
	if not private:

		user = message.author
		sc = get_spam_chart()

		try:
			if message.guild.id not in sc:
				sc[message.guild.id] = {}
				spam_chart.cache('spam_chart', sc)
		except AttributeError:
			pass

		safe = False
		guild = message.guild
		try:
			banWords = (await read('banWords', True, False))[guild.id]
		except KeyError:
			banWords = await read('banWords', True, False)

			banWords[guild.id] = []

			await write('banWords', banWords, False)
			banWords = []
		try:
			banEmojis = (await read('banEmojis', True, False))[guild.id]
		except KeyError:
			banEmojis = await read('banEmojis', True, False)
			banEmojis[guild.id] = []
			await write('banEmojis', banEmojis, False)
			banEmojis = []
		bot_prefix = await read('bot_prefix', False)

		channel = message.channel

		prefix_length = len(bot_prefix)

	if message.author != client.user and private:
		await mod_mail(message, client)
	elif message.author != client.user:

		try:
			base_duration = (await read('duration'))[guild.id]
		except KeyError:

			bd = await read('duration')
			bd[guild.id] = 5
			await write('duration', bd)
			base_duration = 5

		try:
			offenseDuration = (await read('od'))[guild.id]

		except KeyError:
			od = await read('od')
			od[guild.id] = 5
			await write('od', od)
			offenseDuration = (await read('od'))[guild.id]
		moderator = discord.utils.get(message.guild.roles, id=525677521430118411)
		content = message.content
		user = message.author
		try:
			mri = (await read('mute-role-id'))[guild.id]
		except KeyError:
			mri = (await get_muted_role(guild)).id
			mute_id_dict = await read('mute-role-id')
			mute_id_dict[guild.id] = mri
			await write('mute-role-id', mute_id_dict)

		try:
			base_duration = (await read('duration'))[guild.id]
		except KeyError:

			bd = await read('duration')
			bd[guild.id] = 5
			await write('duration', bd)
			base_duration = 5

		if message.content.startswith('?'):

			content = message.content
			user = message.author
			try:
				mri = (await read('mute-role-id'))[guild.id]
			except KeyError:
				mri = (await get_muted_role(guild)).id

			if user.id == 487258918465306634 or user.id == 527937324865290260:
				if content.startswith(bot_prefix):
					# if content[prefix_length:].startswith('killall'):
					# sys.exit()
					if content[prefix_length:].startswith('eval'):
						content = content.replace(' ', '|', 1).split('|')
						try:
							await channel.send(eval(content[1]))
						except discord.errors.HTTPException:
							await channel.send('Task completed')
			if guild.id == 437048931827056642 and user.guild_permissions.administrator:

				if content.startswith(bot_prefix):
					if content[prefix_length:].startswith('prefix'):
						await write(
							'bot_prefix',
							str(content[prefix_length + 7:])
						)

						await channel.send(
							'The Bot prefix is now ' + str(
								content[prefix_length + 7:]
							)
						)

						bot_prefix = await read('bot_prefix', False)

						game = discord.Game(
							name='The bot prefix is: ' + bot_prefix
						)
						await client.change_presence(activity=game)
			content = message.content
			if content.startswith(bot_prefix):
				cmd = content[prefix_length:].lower().split(' ')[0].lower()
				if cmd in cmdDict:
					args = content[prefix_length + len(cmd) + 1:].split(' ')
					try:
						await cmdDict[cmd](args, message, client)
					except TypeError:
						await cmdDict[cmd](args, message)
			if user.guild_permissions.administrator or moderator in user.roles:

				if content.startswith(bot_prefix):
					if content[prefix_length:].lower().startswith('banlist'):
						bl = '\n'.join(banWords)
						be = '\n'.join(banEmojis) + '\n'
						msg = '```fix\nWords:\n' + bl + '\n' + 'Reactions:\n' + be + '```'
						await channel.send(msg)
					elif content[prefix_length:].lower().startswith('banword'):
						content = content[prefix_length:][8:]
						banWords.append(content.lower())
						fullBanWords = await read('banWords', True, False)
						fullBanWords[guild.id] = banWords
						await write('banWords', fullBanWords, False)
						await channel.send('`' + content + '` Has been banned')
						safe = True
					elif content[prefix_length:].lower().startswith('unbanword'):
						content = content[prefix_length:][10:]
						print(content)
						try:
							print(content.lower())
							banWords.remove(content.lower())
							fullBanWords = await read('banWords', True, False)
							fullBanWords[guild.id] = banWords
							await write('banWords', fullBanWords, False)
							await channel.send('`' + content + '` Has been unbanned')
						except KeyError:
							await channel.send(f'`{content[1].lower()}` is not in the banlist.')
						safe = True
					elif content[prefix_length:].lower().startswith('banreaction'):
						content = content[12:]
						banEmojis.append(content[1])
						fullBanEmojis = await read('banEmojis', True, False)
						fullBanEmojis[guild.id] = banEmojis
						await write('banEmojis', fullBanEmojis, False)
						await channel.send('`' + content[1] + '` reaction been banned')
					elif content[prefix_length:].lower().startswith('unbanreaction'):
						content = content[14:]
						try:
							banEmojis.remove(content[1])
							fullBanEmojis = await read('banEmojis', True, False)
							fullBanEmojis[guild.id] = banEmojis
							await write('banEmojis', fullBanEmojis, False)
							await channel.send('`' + content[1] + '` reaction been unbanned')
						except ValueError:
							await channel.send('`' + content[1] + '` is not in the reaction list!')

		content = message.content.lower()

		#  afterdate = datetime.datetime.now()
		#  await message.channel.send(str(afterdate-beforedate))
		#
		# MESSAGE SPAM/ BANNED CONTENT DETECTING
		#
		#

		if not private:
			if user.guild_permissions.administrator:
				safe = True
			if not safe:
				for char in ignoredChars:
						content = content.replace(char, '')

				full_phrase_limit = (await read('pl'))
				if guild.id in full_phrase_limit:
					phrase_limit = full_phrase_limit[guild.id]
				else:
					phrase_limit = 10
					full_phrase_limit[guild.id] = 10
					await write('pl', full_phrase_limit)
				banned_word = False
				for a in banWords:
						a = a.lower()
						begin = content.startswith(a)
						end = content.endswith(a)
						if ' ' + a + ' ' in content or begin or end:
							banned_word = True
				full_mention_limit = (await read('ml'))

				if guild.id in full_mention_limit:
					mention_limit = full_mention_limit[guild.id]

				else:
					mention_limit = 5
					full_mention_limit[guild.id] = 5
					await write('ml', full_mention_limit)

				if len(message.mentions) > mention_limit:
					mention_spam = True
				else:
					mention_spam = False
				full_emoji_limit = await read('em')
				if guild.id in full_emoji_limit:
					emoji_limit = full_emoji_limit[guild.id]
				else:
					emoji_limit = 30
					full_emoji_limit[guild.id] = emoji_limit
					await write('em', full_emoji_limit)
				if emoji_count(message.content) > emoji_limit:
					emoji_max = True

				else:
					emoji_max = False

				has_link = any(url in message.content for url in [
					'discord.gg/', 'discordapp.com/invite/']
				)

				groupie = banned_word or has_link or emoji_max or mention_spam

				if is_repeating(message.content, phrase_limit) or groupie:

					await message.delete()

					log_offense(message.author.id, guild.id, offenseDuration * 2, message)

					if banned_word:
						msg = await channel.send(
							f'<@!{user.id}> That word is not allowed!'
						)
					elif has_link:
						msg = await channel.send(
							f'<@!{user.id}> invite links are not allowed!'
						)
					elif emoji_max:
						msg = await channel.send(
							f'<@!{user.id}> there are too many emojis in your message!'
						)
					elif mention_spam:
						msg = await channel.send(
							f'<@!{user.id}> there are too many @mentions in your message!'
						)
					else:
						msg = await channel.send(
							f'<@!{user.id}> please dont spam!'
						)

				guildId = guild.id
				userId = user.id
				full_offenseLimit = await read('ol')

				if guild.id in full_offenseLimit:
					offenseLimit = full_offenseLimit[guild.id] + 1
				else:
					offenseLimit = 6
					full_offenseLimit[guild.id] = 5
					await write('ol', full_offenseLimit)

				muteList = await read('muteList')
				if guild.id in muteList:
					guild_muteList = (muteList)[guild.id]
				else:
					muteList[guild.id] = {}
					guild_muteList = {}
					await write('muteList', muteList)

				full_mute_increment = await read('mi')
				if guild.id in full_mute_increment:
					gmi = full_mute_increment[guild.id]
				else:
					gmi = 2
					full_mute_increment[guild.id] = gmi
					await write('mi', full_mute_increment)

				if user.id in guild_muteList:

					offenses = guild_muteList[user.id]['Offenses']

					mute_increment = (gmi * offenses + 1)
				else:
					full_mute_increment = await read('mi')
					if guild.id in full_mute_increment:
						gmi = full_mute_increment[guild.id]
					else:
						gmi = 2
						full_mute_increment[guild.id] = gmi
						await write('mi', full_mute_increment)
					offenses = 0
					mute_increment = (gmi * offenses + 1)

					if guild.id in muteList:
						guild_muteList = (muteList)[guild.id]
					else:
						muteList[guild.id] = {}

					await write('muteList', muteList)

				mute_duration = base_duration * mute_increment
				try:
					mri = (await read('mute-role-id'))[guild.id]
				except KeyError:
					pass

				offenses = log_offense(
					message.author.id,
					guild.id,
					offenseDuration,
					message
				)

				spamChart = get_spam_chart()

				if offenseLimit - 1 == offenses:
					dm_channel = await user.create_dm()
					text = f'<@!{str(userId)}> please stop spamming. You have been warned'
					embed = discord.Embed(
						title="Stop Spamming",
						description=text,
						color=0xff0000
					)
					await dm_channel.send(embed=embed)

				#########################

				if offenseLimit <= len(spamChart[guildId][userId]):
					muted = await get_muted_role(guild)

					await user.add_roles(muted, reason='User was spamming')
					author = message.author
					if (await get_muted_role(guild)) not in author.roles:

						await log(f"<@{author.id}> has been automatically muted", guild)
					muteList = await read('muteList')

					guild_muteList = (await read('muteList'))[guild.id]

					print(f'{str(mute_duration)}d')
					timeup = commands.moderation_tools.findDate(str(f'{str(mute_duration)}m'))

					if user.id in guild_muteList:
						if (await get_muted_role(guild)) not in author.roles:
							guild_muteList[user.id]['Offenses'] += 1
							guild_muteList[user.id]['timeup'] = timeup

					else:
						guild_muteList[user.id] = {'Offenses': 1, 'timeup': timeup}

					muteList[guild.id] = guild_muteList
					await write('muteList', muteList)
					await message.delete()

				try:

					yesAnnotherThing = str(repr(content).encode('ascii'))

					if content not in (yesAnnotherThing).replace('\\n', '\n'):
						await message.delete()
						await channel.send(
							f"Illegal character detected in <@!{user.id}>'s message."
						)
				except UnicodeEncodeError:
					pass
		mark_time('>>>>>>check end')

		thinger = ast.literal_eval(str(await read('test_thinger')))

		thinger["thinger"].append(eval(str(datetime.datetime.now() - startTime)[5:]))
		await write('test_thinger', thinger)


@client.event
async def on_reaction_add(reaction, user):
	if user.guild_permissions.administrator:
		safe = True
	else:
		safe = False
	if not safe:
		banEmojis = await read('banEmojis', True, False)
		guild = reaction.message.guild
		if str(reaction) in banEmojis[guild.id]:
			await reaction.remove(user)
			await reaction.message.channel.send(
				f'<@!{str(user.id)}> That reaction is banned!'
			)


async def checkBan():
	global client
	banList = await read('banList')
	delList = []
	for guild_list in banList:
		for userId in banList[guild_list]:
			date = banList[guild_list][userId]
			date = datetime.datetime.strptime(date, "%Y-%m-%w-%W %H:%M:%S")
			if datetime.datetime.now() >= date:
				delList.append([guild_list, userId])

	for a in delList:
		guild = client.get_guild(a[0])
		banEntry = await guild.bans()
		for each in banEntry:
			if each.user.id == a[1]:
				user = each.user
				break
		if not user:
			print(f'user {a[1]} not found')
			return
		print('unbanning')
		username = user.display_name
		await log(
			f'`{username}` has been unbanned because their time is up',
			guild
		)
		await guild.unban(user=user, reason='User\'s time was up')
		del banList[a[0]][a[1]]

	await write('banList', banList)


async def checkMute():
	global client
	mute_list = await read('muteList')
	del_list = []
	for guild_list in mute_list:
		for userId in mute_list[guild_list]:

			date = mute_list[guild_list][userId]["timeup"]
			date = datetime.datetime.strptime(date, "%Y-%m-%w-%W %H:%M:%S")
			if datetime.datetime.now() >= date:
				del_list.append([guild_list, userId])

	for a in del_list:
		guild = client.get_guild(a[0])
		member_id_list = [member.id for member in guild.members]
		if a[1] not in member_id_list:
			del mute_list[a[0]][a[1]]
		else:
			user = guild.get_member(a[1])
			print('unmuting')
			username = user.display_name
			await log(
				f'`{username}` has been unmuted because their time is up',
				guild
			)
			del mute_list[a[0]][a[1]]
			await user.remove_roles(await get_muted_role(guild))

	await write('muteList', mute_list)


async def bgTasks():

	while True:
		await checkMute()
		await checkBan()
		await check_expire(client)
		await asyncio.sleep(1)
keep_alive.keep_alive()

key = os.environ.get('KEY')
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)
