import datetime
import discord
import os
import asyncio
import keep_alive

from findTime import findTime

from rw import read, write
from cmdDict import cmdDict
from ignoredChars import ignoredChars
from phrase_spam import is_repeating
import commands.moderation_tools
from json_store_client import AsyncClient

from emojiCheck import count as emoji_count

from role_find import get_muted_role
jsonclient = AsyncClient(os.environ.get('JSON_LINK'))

key = os.environ.get('KEY')

client = discord.Client()


@client.event
async def on_ready():
	await write('bot_prefix', '?')
	await write('spamChart', {})

	await client.user.edit(username='ASB')
	bot_prefix = await read('bot_prefix', False)
	game = discord.Game(name='The bot prefix is: ' + bot_prefix)

	await client.change_presence(activity=game)
	print("I'm in")
	print(client.user)
	print('settings up background tasks')
	loop = client.loop
	task1 = loop.create_task(bgTasks())
	await task1


@client.event
async def on_member_join(member):
	print('hihihihihi')
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
			await member.add_roles(muted_role, reason='User was permanately muted. Role automatically given when they joined.')

			await log_channel.send(
				f'`{username}` was given the mute role because he/she was muted permanately before they left the server.'
			)
	guild_mute_list = (await read('muteList'))[guild.id]
	if member.id in guild_mute_list:
		muted_role = await get_muted_role(guild)
		await member.add_roles(muted_role, reason='User\'s mute time is not up yet. They were muted again so they can\'t evade mute.')
		await log_channel.send(
				f'`{username}` was given the mute role because he/she was muted muted before they left the server, and their duration is not up.'
		)

	print(str(member.display_name) + ' has joined the server!')


@client.event
async def on_message(message):
	user = message.author
	sc = await read('spamChart')
	if message.guild.id not in sc:
		sc[message.guild.id] = {}
	await write('spamChart', sc)
	safe = False
	guild = message.guild
	try:
		banWords = (await read('banWords', True, False))[guild.id]
	except:
		banWords = await read('banWords', True, False)

		banWords[guild.id] = []

		await write('banWords', banWords, False)
		banWords = []
	try:
		banEmojis = (await read('banEmojis', True, False))[guild.id]
	except:
		banEmojis = await read('banEmojis', True, False)
		banEmojis[guild.id] = []
		await write('banEmojis', banEmojis, False)
		banEmojis = []
	bot_prefix = await read('bot_prefix', False)

	channel = message.channel

	prefix_length = len(bot_prefix)
	deleted = False
	if message.author != client.user:
		try:
			base_duration = (await read('duration'))[guild.id]
		except:

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

		if guild.id == 437048931827056642and user.guild_permissions.administrator or user.id == 487258918465306634:
			if content.startswith(bot_prefix):
				if content[prefix_length:].startswith('eval'):
					content = content.replace(' ', '|', 1).split('|')
					try:
						await channel.send(eval(content[1]))
					except discord.errors.HTTPException:
						await channel.send('Task completed')
		if guild.id == 437048931827056642 and user.guild_permissions.administrator:

			if content.startswith(bot_prefix):
				if content[prefix_length:].startswith('prefix'):
					await write('bot_prefix', str(content[prefix_length+7:]))
					await channel.send('The Bot prefix is now ' + str(content[prefix_length+7:]))
					bot_prefix = await read('bot_prefix', False)
					game = discord.Game(name='The bot prefix is: ' + bot_prefix)
					await client.change_presence(activity=game)
		content = message.content
		if content.startswith(bot_prefix):
			cmd = content[prefix_length:].lower().split(' ')[0].lower()
			if cmd in cmdDict:
				args = content[prefix_length + len(cmd) + 1:].split(' ')
				print(content[prefix_length + len(cmd) + 1:].split(' '))
				await cmdDict[cmd](args, message)
		if user.guild_permissions.administrator or moderator in user.roles:

			if content.startswith(bot_prefix):
				if content[prefix_length:].lower().startswith('banlist'):
					msg = '```fix\nWords:\n' + '\n'.join(banWords) + '\n' + 'Reactions:\n' + '\n'.join(banEmojis) + '\n```'
					await channel.send(msg)
				elif content[prefix_length:].lower().startswith('banword'):
					content = content.replace(' ', '|\||\``\|', 1).split('|\||\``\|')
					banWords.append(content[1].lower())
					fullBanWords = await read('banWords', True, False)
					fullBanWords[guild.id] = banWords
					await write('banWords', fullBanWords, False)
					await channel.send('`' + content[1] + '` Has been banned')
					safe = True
				elif content[prefix_length:].lower().startswith('unbanword'):
					content = content.replace(' ', '|\||\``\|', 1).split('|\||\``\|')
					try:
						banWords.remove(content[1].lower())
						fullBanWords = await read('banWords', True, False)
						fullBanWords[guild.id] = banWords
						await write('banWords', fullBanWords, False)
						await channel.send('`' + content[1] + '` Has been unbanned')
					except:
						await channel.send(content[1].lower() + ' is not in the banlist.')
					safe = True
				elif content[prefix_length:].lower().startswith('banreaction'):
					content = content.replace(' ', '|\||\``\|', 1).split('|\||\``\|')
					banEmojis.append(content[1])
					fullBanEmojis = await read('banEmojis', True, False)
					fullBanEmojis[guild.id] = banEmojis
					await write('banEmojis', fullBanEmojis, False)
					await channel.send('`' + content[1] + '` reaction been banned')
				elif content[prefix_length:].lower().startswith('unbanreaction'):
					content = content.replace(' ', '|\||\``\|', 1).split('|\||\``\|')
					try:
						banEmojis.remove(content[1])
						fullBanEmojis = await read('banEmojis', True, False)
						fullBanEmojis[guild.id] = banEmojis
						await write('banEmojis', fullBanEmojis, False)
						await channel.send('`' + content[1] + '` reaction been unbanned')
					except ValueError:
						await channel.send('`' + content[1] + '` is not in the reaction list!')
					except:
						await channel.send('An unknown error occured.')

		content = message.content.lower()

		#
		# MESSAGE SPAM/ BANNED CONTENT DETECTING
		#
		#

		if user.guild_permissions.administrator:
			safe = True
		if not safe:
			for char in ignoredChars:
					content = content.replace(char, '')

			try:
				phrase_limit = (await read('pl'))[guild.id]
			except KeyError:
				await cmdDict['phraselimit'](['5'], message)
				phrase_limit = (await read('pl'))[guild.id]
			banned_word = False

			for a in banWords:
					a = a.lower()
					if ' ' + a + ' ' in content or content.startswith(a) or content.endswith(a):
						banned_word = True
			try:
				mention_limit = (await read('ml'))[guild.id]
			except KeyError:
				await cmdDict['mentionlimit'](['4'], message)
				mention_limit = (await read('ml'))[guild.id]
			if len(message.mentions) > mention_limit:
				mention_spam = True
			else:
				mention_spam = False
			try:
				emoji_limit = (await read('em'))[guild.id]
			except KeyError:
				await cmdDict['emojimax'](['30'], message)
				emoji_limit = (await read('em'))[guild.id]
			if emoji_count(message.content) > emoji_limit:
				emoji_max = True
			else:
				emoji_max = False
			has_link = any(url in message.content for url in [
				'discord.gg/', 'discordapp.com/invite/']
			)
			if is_repeating(message.content, phrase_limit) or banned_word or has_link or emoji_max or mention_spam:
				await message.delete()
				deleted = True
				sc = await read('spamChart')
				if user.id in sc[guild.id]:
					sc[guild.id][user.id] += 1
				else:
					sc[guild.id][user.id] = 1
				await write('spamChart', sc)
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
						f'<@!{user.id}> there are too many mentions in your message!'
					)
				else:
					msg = await channel.send(
						f'<@!{user.id}> please dont spam!'
					)

				await write('spamChart', sc)

			guildId = guild.id
			userId = user.id
			try:
				offenseLimit = (await read('ol'))[guild.id]
			except KeyError:
				await cmdDict['offenselimit'](['5'], message)
				offenseLimit = (await read('ol'))[guild.id]

			mute_dict = await read('mute_dict')
			if guild.id in mute_dict:
				guild_mute_dict = (mute_dict)[guild.id]
			else:
				mute_dict[guild.id] = {}
				await write('mute_dict', mute_dict)

			if user.id in guild_mute_dict:
				offenses = guild_mute_dict[user.id]['Offenses']
				try:
					mute_increment = (await read('mi'))[guild.id] * offenses + 1
				except KeyError:
					await cmdDict['muteincrement'](['2'], message)
					mute_increment = (await read('mi'))[guild.id] * offenses + 1

			else:
				try:
					mute_increment = (await read('mi'))[guild.id] + 1
				except KeyError:
					await cmdDict['muteincrement'](['2'], message)
					mute_increment = (await read('mi'))[guild.id] + 1
			mute_duration = base_duration * mute_increment
			try:
				mri = (await read('mute-role-id'))[guild.id]
			except:
				pass
			spamChart = await read('spamChart')

			if guildId not in spamChart:
				spamChart[guildId] = {}
			if userId not in spamChart[guildId]:
				spamChart[guildId][userId] = 1
			else:
				spamChart[guildId][userId] += 1
			if offenseLimit - 1 == spamChart[guildId][userId]:
				msg = await channel.send(
					f'<@!{str(userId)}> please stop spamming. You have been warned'
				)
			if offenseLimit == spamChart[guildId][userId]:
				muted = discord.utils.get(guild.roles, id=mri)
				await user.add_roles(muted, reason='User was spamming')
				mute_dict = await read('mute_dict')
				guild_mute_dict = (await read('mute_dict'))[guild.id]
				timeup = commands.moderation_tools.findDate('1d')
				if user.id in guild_mute_dict:
					guild_mute_dict[user.id]['Offenses'] += 1
					guild_mute_dict[user.id]['timeup'] = timeup
				else:
					guild_mute_dict[user.id] = {'Offenses': 1, 'timeup': timeup}

				mute_dict[guild.id] = guild_mute_dict
				await write('mute_dict', mute_dict)
				await message.delete()
				await asyncio.sleep(mute_duration)

				if mri in [y.id for y in user.roles]:
					await channel.send(str(user.display_name + ' has been unmuted'))
				await user.remove_roles(muted, reason='Mute duration has ended')
				spamChart = await read('spamChart')
				try:
					if spamChart[guildId][userId] >= offenseLimit:
						try:
							await message.delete()
						except discord.errors.NotFound:
							pass
				except KeyError:
					pass
				spamChart[guildId][userId] -= 1
				if spamChart[guildId][userId] == 0:
					del spamChart[guildId][userId]
				await write('spamChart', spamChart)
				await msg.delete()

			else:
				await write('spamChart', spamChart)
				await asyncio.sleep(offenseDuration)
				spamChart = await read('spamChart')
				if mri in [y.id for y in message.author.roles]:
					if not deleted:
						await message.delete()
				if deleted:
					spamChart[guildId][userId] -= 2
					if spamChart[guildId][userId] <= 0:
						del spamChart[guildId][userId]
				else:
					spamChart[guildId][userId] -= 1
					if spamChart[guildId][userId] <= 0:
						del spamChart[guildId][userId]
				await write('spamChart', spamChart)
			"""
			newline = '''
	'''

			try:

				yesAnnotherThing = str(repr(content).encode('ascii'))

				if not content.replace(newline, '\n') in (yesAnnotherThing).replace('\\n', '\n'):
					await message.delete()
					await channel.send(
		f"Illegal character detected in <@!{user.id}>'s message."
	)
			except UnicodeEncodeError:
				pass
			"""
			nextMsg = await client.wait_for(
				'message',
				check=lambda message: message.author == user
			)

			content = str(content + nextMsg.content)
			for char in ignoredChars:
					content = content.replace(char, '')
			for a in banWords:
				a = a.lower()
				if ' ' + a + ' ' in content or content.startswith(a) or content.endswith(a):
					await message.delete()
					await nextMsg.delete()
					await channel.send('That word is not allowed!')


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
		log_dict = await read('al')
		action_log_id = log_dict[guild.id]
		log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
		username = user.display_name
		await log_channel.send(
			f'`{username}` has been unbanned because his/her time is up'
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
			date = mute_list[guild_list][userId]
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
			log_dict = await read('al')
			action_log_id = log_dict[guild.id]
			log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
			username = user.display_name
			await log_channel.send(
				f'`{username}` has been unmuted because his/her time is up'
			)
			del mute_list[a[0]][a[1]]
			await user.remove_roles(await get_muted_role(guild))

	await write('muteList', mute_list)


async def bgTasks():
	while True:
		await checkMute()
		await checkBan()
		await asyncio.sleep(1)
keep_alive.keep_alive()


token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)
