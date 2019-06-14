import discord
import os
import asyncio
import keep_alive
import commands
from findTime import findTime
from rw import read, write
from cmdDict import cmdDict
from ignoredChars import ignoredChars
from json_store_client import *

jsonclient = AsyncClient(os.environ.get('JSON_LINK'))

key = os.environ.get('KEY')
# thing = encode(key, '{}')

keyList = [
	'banWords',
	'banEmojis',
	'spamChart'
	]

# Constants:
INITIAL_BOT_PREFIX = '?'

ADMINS = [
	487258918465306634
	]

GUILDS = [
	437048931827056642
	]

# reserved for a {command_name(str): command(func)} dictionary for importable commands
COMMANDS = {
	'eval': commands.evaluate
	}
	
COMMAND_FRAMEWORK_DONE = False

client = discord.Client()


@client.event
async def on_ready():
	current_prefix = await read('bot_prefix', None)

	if not current_prefix:	# prefix hasn't been set before, new db
		await write('bot_prefix', INITAL_BOT_PREFIX)

	game = discord.Game(name='The bot prefix is: ' + current_prefix)
	await client.change_presence(activity=game)

	for a in keyList:
		if not read(a, None):
			await write(a, {}, False)

	print("I'm in")
	print(client.user)


@client.event
async def on_message(message):
	# context
	user = message.author
	safe = False
	guild = message.guild
	content = message.content
	bot_prefix = await read('bot_prefix', False)
	channel = message.channel
	prefix_length = len(bot_prefix)
	
	# i don't talk to bots
	
	if user.bot:
		return
	
	# delete messages with certain words
	
	genericBanWords = await read('banWords', True, False)
	banWords = genericBanWords.get(guild.id, None)
	
	if not banWords:
		genericBanWords[guild.id] = []
		
		await write('banWords', genericBanWords, False)
		banWords = []
	
	
	if not safe:
		badWords = [word for word in banWords 
						if f' {word} ' in content or content.startswith(a) or content.endswith(a)]
		
		if len(badWords) >= 1:
			await message.delete()
			await channel.send('Those words are not allowed!' if len(badWords) > 1 else 'That word is not allowed!')
			return
	
	
	
	# command framework
	
	if content.startswith(bot_prefix) and COMMAND_FRAMEWORK_DONE:
		full_command = content.lower()
		command_name = full_command.split(' ')[0][prefix_length:]
		args = content.split(' ')[1:] # preserve case
		
		ctx = {
			'message': message,
			'guild': guild,
			'channel': channel,
			'prefix': prefix,
			'author': user
		}
		
		command_func = COMMANDS.get(command)
		
		if command_func:
			await command_func(ctx, args)
			return
		else:
			await channel.send('`command not found`')
			return
	
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
	except:
		await channel.send('No muted role set!')
		pass

	if guild.id in GUILDS and user.guild_permissions.administrator or user.id in ADMINS:
		if content.startswith(bot_prefix):
			if content[prefix_length:].startswith('eval'):
				content = content.replace(' ', '|', 1).split('|')
				try:
					await channel.send(eval(content[1]))
				except discord.errors.HTTPException:
					await channel.send('Task completed')
	if guild.id in GUILDS and user.guild_permissions.administrator:

		if content.startswith(bot_prefix):
			if content[prefix_length:].startswith('prefix'):
				await write('bot_prefix', str(content[prefix_length + 7:]))
				await channel.send('The Bot prefix is now ' + str(content[prefix_length + 7:]))
				bot_prefix = await read('bot_prefix', False)
				game = discord.Game(name='The bot prefix is: ' + bot_prefix)
				await client.change_presence(activity=game)
	content = message.content
	
	

	if user.guild_permissions.administrator or moderator in user.roles:

		if content.startswith(bot_prefix):
			cmd = content[prefix_length:].lower().split(' ')[0].lower()
			if cmd in cmdDict:
				args = content[prefix_length + len(cmd) + 1:].split(' ')
				print(content[prefix_length + len(cmd) + 1:].split(' '))
				await cmdDict[cmd](args, message)
			if content[prefix_length:].lower().startswith('muteid'):
				content = content.split(' ')
				muteIds = await read('mute-role-id')
				muteIds[guild.id] = int(content[1])
				await write('mute-role-id', muteIds)

			elif content[prefix_length:].startswith('permamute'):
				content = content.replace(' ', '|||||', 2)
				content = content.split('|||||')
				if len(content) == 3:
					if content[1][:3] != '<@!':
						userId = int(content[1][2:][:-1])
					else:
						userId = int(content[1][3:][:-1])
					muted = discord.utils.get(guild.roles, id=mri)
					muteUser = guild.get_member(userId)
					await muteUser.add_roles(muted, reason=content[2])
					await channel.send(muteUser.display_name + ' has been muted')
				elif len(content) == 2:
					if content[1][:3] != '<@!':
						userId = int(content[1][2:][:-1])
					else:
						userId = int(content[1][3:][:-1])
					muted = discord.utils.get(guild.roles, id=mri)
					muteUser = guild.get_member(userId)
					await muteUser.add_roles(muted, reason=user.display_name + ' muted him/her')
					await channel.send(muteUser.display_name + ' has been muted')
				else:
					await channel.send(f'Invalid syntax. Example: {bot_prefix}mute @jon bc i can lol')
			elif content[prefix_length:].lower().startswith('banlist'):
				msg = '```fix\nWords:\n' + '\n'.join(banWords) + '\n' + 'Reactions:\n' + '\n'.join(banEmojis) + '\n```'
				await channel.send(msg)
			elif content[prefix_length:].lower().startswith('banword'):
				content = content.replace(' ', '|\||\``\|', 1).split('|\||\``\|')
				banWords.append(content[1].lower())
				fullBanWords = await read('banWords')
				fullBanWords[guild.id] = banWords
				await write('banWords', fullBanWords)
				await channel.send('`' + content[1] + '` Has been banned')
				safe = True
			elif content[prefix_length:].lower().startswith('unbanword'):
				content = content.replace(' ', '|\||\``\|', 1).split('|\||\``\|')
				try:
					banWords.remove(content[1].lower())
					fullBanWords = await read('banWords')
					fullBanWords[guild.id] = banWords
					await write('banWords', fullBanWords)
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
			elif content[prefix_length:].split(' ')[0] == 'mute':
				content = content.replace(' ', '|||||', 3)
				content = content.split('|||||')
				if len(content) == 4:
					if content[1][:3] != '<@!':
						userId = int(content[1][2:][:-1])
					else:
						userId = int(content[1][3:][:-1])
					muted = discord.utils.get(guild.roles, id=mri)
					muteUser = guild.get_member(userId)
					await muteUser.add_roles(muted, reason=content[3])
					await channel.send(muteUser.display_name + ' has been muted')

					await asyncio.sleep(findTime(content[2]))

					await muteUser.remove_roles(muted, reason='Mute time has ended')
					await channel.send('<@!' + str(muteUser.id) + '>  has been unmuted, because his/her time is up.')
				elif len(content) == 3:
					if content[1][:3] != '<@!':
						userId = int(content[1][2:][:-1])
					else:
						userId = int(content[1][3:][:-1])
					muted = discord.utils.get(guild.roles, id=mri)
					muteUser = guild.get_member(userId)
					await muteUser.add_roles(muted, reason=user.display_name + ' muted him/her')
					await channel.send(muteUser.display_name + ' has been muted')
					await asyncio.sleep(findTime(content[2]))

					await muteUser.remove_roles(muted, reason='Mute time has ended')
					await channel.send('<@!' + str(muteUser.id) + '>  has been unmuted, because his/her time is up.')
				else:
					await channel.send(f'Invalid syntax. Example: {bot_prefix}mute @jon 1 bc i can lol')
			elif content[prefix_length:].startswith('unmute'):
				content = content.replace(' ', '|||||', 2)
				content = content.split('|||||')
				if len(content) == 3:
					if content[1][:3] != '<@!':
						userId = int(content[1][2:][:-1])
					else:
						userId = int(content[1][3:][:-1])
					muted = discord.utils.get(guild.roles, id=mri)
					muteUser = guild.get_member(userId)
					await muteUser.remove_roles(muted, reason=content[2])
					await channel.send('<@!' + str(muteUser.id) + '> has been unmuted')
				elif len(content) == 2:
					if content[1][:3] != '<@!':
						userId = int(content[1][2:][:-1])
					else:
						userId = int(content[1][3:][:-1])
					muted = discord.utils.get(guild.roles, id=mri)
					muteUser = guild.get_member(userId)
					await muteUser.remove_roles(muted, reason=user.display_name + ' unmuted him/her')
					await channel.send('<@!' + str(muteUser.id) + '> has been unmuted')
				else:
					await channel.send(f'Invalid syntax. Example: {bot_prefix}unmute @jon bc i can lol')
	content = message.content.lower()
	for char in ignoredChars:
		content = content.replace(char, '')

	guildId = guild.id
	userId = user.id
	offenseLimit = 5
	mute_duration = base_duration
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
		await channel.send(f'<@!{str(userId)}> please stop spamming. You have been warned')
	if offenseLimit == spamChart[guildId][userId]:
		muted = discord.utils.get(guild.roles, id=mri)
		await user.add_roles(muted, reason='User was spamming')
		await message.delete()
		await asyncio.sleep(mute_duration)

		if mri in [y.id for y in user.roles]:
			await channel.send(str(user.display_name + ' has been  unmuted'))
		await user.remove_roles(muted, reason='Mute duration has ended')
		spamChart = await read('spamChart')
		try:
			if spamChart[guildId][userId] >= offenseLimit:
				await message.delete()
		except KeyError:
			pass
		spamChart[guildId][userId] -= 1
		if spamChart[guildId][userId] == 0:
			del spamChart[guildId][userId]
		await write('spamChart', spamChart)
	else:
		await write('spamChart', spamChart)
		await asyncio.sleep(offenseDuration)
		spamChart = await read('spamChart')
		if mri in [y.id for y in message.author.roles]:
			await message.delete()
		spamChart[guildId][userId] -= 1
		if spamChart[guildId][userId] == 0:
			del spamChart[guildId][userId]
		await write('spamChart', spamChart)

	delete = False
	newline = '''
'''

	def check(m):
		return m.content == 'hello' and m.channel == channel

	try:

		yesAnnotherThing = str(repr(content).encode('ascii'))

		if not content.replace(newline, '\n') in (yesAnnotherThing).replace('\\n', '\n'):
			await message.delete()
			await channel.send(f'Illegal character detected in <@!{user.id}>\'s message.')
	except UnicodeEncodeError:
		pass

	nextMsg = await client.wait_for('message', check=lambda message: message.author == user)

	msgList = [message]
	count = 0
	done = False
	unusedWords = []
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
	banEmojis = await read('banEmojis', True, False)
	guild = reaction.message.guild
	if str(reaction) in banEmojis[guild.id]:
		await reaction.remove(user)
		await reaction.message.channel.send(f'<@!{str(user.id)}> That reaction is banned!')


keep_alive.keep_alive()

token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)
