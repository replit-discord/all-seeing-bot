import discord
from at import argTest
from rw import read, write
from checkTrust import checkTrust
from findTime import findTime
helpMsg = discord.Embed(title='Customization', description='''
**`muteduration <time>`:**  Sets the base mute duration. (Default: `5m`)

**`offenseduration <time>`:**  Sets how long an offense/msg for spam count lasts. (Default: `5s`)

**`offenselimit <ammount>`:**  Sets how many offenses a user can make before being muted.  (Default: `5`)

**`muteincrement <ammount>`:**  Sets how much mute time increses if muted multiple ammount of times in a time period.  (Default: `2`)

**`phraselimit <ammount>`:**  Sets how many times a phrase can be repeated in a row in a message.  (Default: `10`)

**`emojimax <ammount>`:**  Sets the maximum ammount of emojis per message.  (Default: `30`)

**`mentionlimit <ammount>`:**  Sets the maximum ammount of mentions in a message.   (Default: `5`)

**`actionlog <channel mention>`:**  Sets the action log channel.

**`trustrole <role id/role ping>`:** Trusts a role

**`modmail <channel mention>`:**  Sets the mod mail channel.
(any of these commands can be used without args to get the current value)

**`muterole <role id/role ping>`:**  Sets the muted role to the choses role.  (By default, will look for a role named `muted` but if there isnt one it will create one)
''', color=0x00ff80)


async def log(text, msg, title='Customization'):
	guild = msg.guild
	log_embed = discord.Embed(
		title=title,
		description=text,
		color=0x00ff80
	)
	log_dict = await read('al')
	action_log_id = log_dict[guild.id]
	log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
	await log_channel.send(embed=log_embed)


async def trust_role(args, msg):
	author = msg.author
	guild = msg.guild
	channel = msg.channel
	failed = False
	if author.guild_permissions.administrator:
		trust_roles = await read('td')
		if guild.id not in trust_roles:
			guild_trust_roles = []
		else:
			guild_trust_roles = trust_roles[guild.id]
		if len(msg.role_mentions) == 1:
			user_id = msg.role_mentions[0].id
			if user_id not in guild_trust_roles:
				role_name = msg.role_mentions[0].name
				guild_trust_roles.append(user_id)
			else:
				failed = True
		else:
			user_id = int(args[0])
			if user_id not in guild_trust_roles:
				guild_trust_roles.append(user_id)
				role_name = discord.utils.get(guild.roles, id=user_id)
			else:
				failed = True
		if not failed:
			await channel.send('Role has been trusted.')
		else:
			await channel.send('Role is already trusted!')
		trust_roles[guild.id] = guild_trust_roles
		await write('td', trust_roles)

		author_name = author.display_name
		log_msg = str(f'`{author_name}` trusted role `{role_name}`')
		if not failed:
			await log(log_msg, msg, 'Trust')


async def mute_role(args, msg):
	author = msg.author
	guild = msg.guild
	channel = msg.channel
	failed = False
	if author.guild_permissions.administrator:
		mute_role = await read('mute-role-id')

		if len(msg.role_mentions) == 1:
			role = msg.role_mentions[0].id
			role.name = msg.role_mentions[0].name
		else:
			role = int(args[0])
			role_name = guild.get_role(role)
		if not failed:
			await channel.send('Muted role has been set.')
		else:
			await channel.send('Muted role is already set!')
		mute_role[guild.id] = role
		await write('mute-role-id', mute_role)

		author_name = author.display_name
		log_msg = str(f'`{author_name}` set mute the role to `{role_name}`')
		if not failed:
			await log(log_msg, msg)


async def untrust_role(args, msg):
	author = msg.author
	guild = msg.guild
	channel = msg.channel
	if author.guild_permissions.administrator:
		trust_roles = await read('td')
		if guild.id not in trust_roles:
			guild_trust_roles = []
		else:
			guild_trust_roles = trust_roles[guild.id]
		invalid = False
		if len(msg.role_mentions) == 1:
			role_id = msg.role_mentions[0].id
		elif len(msg.role_mentions) > 1:
			await channel.send('Invalid args.')
			invalid = True
		else:
			role_id = int(args[0])
		if role_id not in guild_trust_roles:
			invalid = True
			await channel.send('That role is not trusted!')
		if not invalid:
			await channel.send('Role has been reomved from trust list.')
			guild_trust_roles.remove(role_id)
			trust_roles[guild.id] = guild_trust_roles
			await write('td', trust_roles)


async def test_trust(args, msg):
	author = msg.author
	guild = msg.guild
	trusted = await checkTrust(guild, author)
	if trusted:
		await msg.channel.send('True')
	else:
		await msg.channel.send('False')


async def set_duration(args, msg):
	if '' in args:
		args.remove('')

	if msg.author.guild_permissions.administrator:
		types = [
			float
		]

		if not len(args) == 0:
			try:
				args[0] = findTime(args[0])
				if len(args) == 1:
					time = args[0]
					guild = msg.guild
					fdl = await read('duration')
					oT = (await read('od'))[guild.id]
					if args[0] > oT:
						fdl[guild.id] = args[0]
						await write('duration', fdl)

						await msg.channel.send('Default mute duration has been set.')
						log_dict = await read('al')
						if guild.id in log_dict:
							disp_name = msg.author.display_name
							await log(
								f'`{disp_name}` set the default mute duration (Seconds: `{time}`)',
								msg
							)
					else:
						await msg.channel.send(
							f'Mute duration cannot last less time then offense duration (Seconds: `{str(oT)}`)!'
						)
				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} 5s`'
					)
				elif not argTest(types, args):
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid arg types. Example command: `{command} 5s`'
					)
			except ValueError:
				await msg.channel.send(
					f'Invalid arg type. Arg needs to be a time. Example command: `{command} 5s`'
				)
		else:
			cd = (await read("duration"))[msg.guild.id]
			await msg.channel.send(f'Current mute duration is `{cd}`')


async def offense_time(args, msg):
	if'' in args:
		args.remove('')

	if msg.author.guild_permissions.administrator:

		types = [
			float
		]

		if not len(args) == 0:
			time = args[0]
			try:
				args[0] = findTime(args[0])
				if len(args) == 1:
					guild = msg.guild
					od = await read('od')
					mT = (await read('duration'))[guild.id]
					if args[0] < mT:
						od[guild.id] = args[0]
						await write('od', od)
						await msg.channel.send('Offense duration has been set.')
						log_dict = await read('al')
						if guild.id in log_dict:
							disp_name = msg.author.display_name
							await log(
								f'`{disp_name}` set the offense duration to (Seconds: `{time}`)',
								msg
							)
					else:
						await msg.channel.send(
							f'Offense duration cannot be longer than mute time (Seconds: `{str(mT)}`)!'
						)
				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} 5s`'
					)
				elif not argTest(types, args):
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid arg types. Example command: `{command} 5s`'
					)
			except ValueError:
				await msg.channel.send(
					f'Invalid arg type. Arg needs to be a time. Example command: `{command} 5s`'
				)
		else:
			cd = (await read("od"))[msg.guild.id]
			await msg.channel.send(f'Current offense duration is `{cd}`')


async def offense_limit(args, msg):
	try:
		args.remove('')
	except ValueError:
		print('oof', args)
	print(args)
	if msg.author.guild_permissions.administrator:
		types = [
			int
		]

		if not len(args) == 0:
			try:
				args[0] = int(args[0])
				if len(args) == 1:
					guild = msg.guild
					od = await read('ol')

					od[guild.id] = args[0]
					await write('ol', od)
					await msg.channel.send('Offense limit has been set.')
					log_dict = await read('al')
					if guild.id in log_dict:

						disp_name = msg.author.display_name
						await log(
							f'`{disp_name}` set the offense limit to `{args[0]}`',
							msg
						)

				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} 5`'
					)
				elif not argTest(types, args):
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid arg types. Example command: `{command} 5`'
					)
			except IndexError:
						command = msg.content.lower().split(' ')[0]
						await msg.channel.send(
							f'Invalid arg types. Example command: `{command} 5`'
						)
		else:
			cd = (await read("ol"))[msg.guild.id]
			await msg.channel.send(f'Current offense limit is `{cd}`')


async def reset(args, msg):
	if msg.author.id == 487258918465306634:
		try:
			await read(args[0])
			if len(args) == 1:
				await write(args[0], {})
			elif len(args) == 2:
				await write(args[0], args[1])
			else:
				await msg.channel.send('Invalid argument ammount')
		except ValueError:
			pass
	else:
		await msg.channel.send('Only the bot owner can use this command!')


async def Read(args, msg):
	if msg.author.id == 487258918465306634 or msg.author.id == 527937324865290260:
		if len(args) == 1:
			rMessage = await read(args[0])
		elif len(args) == 2:
			rMessage = await read(args[0], eval(args[1]))
		elif len(args) == 3:
			rMessage = await read(args[0], eval(args[1]), eval(args[2]))
		else:
			rMessage = 'Invalid ammount of args'
		await msg.channel.send(rMessage)
	else:
		await msg.channel.send('Only the bot owner can use this command!')


async def Write(args, msg):
	if msg.author.id == 487258918465306634 or msg.author.id == 527937324865290260:
		if len(args) == 2:
			await write(args[0], args[1])
			rMessage = 'Task Complete'
		elif len(args) == 3:
			await write(args[0], args[1], eval(args[2]))
			rMessage = 'Task Complete'
		else:
			rMessage = 'Invalid ammount of args'

		await msg.channel.send(rMessage)

	else:
		await msg.channel.send('Only the bot owner can use this command!')


async def phrase_limit(args, msg):
	try:
		args.remove('')
	except ValueError:
		print('oof', args)
	print(args)
	if msg.author.guild_permissions.administrator:
		types = [
			int
		]

		if not len(args) == 0:
			try:
				args[0] = int(args[0])
				if len(args) == 1:
					guild = msg.guild
					od = await read('pl')

					od[guild.id] = args[0]
					await write('pl', od)
					await msg.channel.send('Phrase limit has been set.')
					log_dict = await read('al')
					if guild.id in log_dict:
						disp_name = msg.author.display_name
						await log(
							f'`{disp_name}` set the phrase limit to `{args[0]}`',
							msg
						)

				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} 5`'
					)
				elif not argTest(types, args):
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid arg types. Example command: `{command} 5`'
					)
			except IndexError:
						command = msg.content.lower().split(' ')[0]
						await msg.channel.send(
							f'Invalid arg types. Example command: `{command} 5`'
						)
		else:
			cd = (await read("pl"))[msg.guild.id]
			await msg.channel.send(f'Current phrase limit is `{cd}`')


async def mute_increment(args, msg):
	try:
		while '' in args:
			args.remove('')
	except ValueError:
		print('oof', args)
	print(args)
	if msg.author.guild_permissions.administrator:
		types = [
			float
		]

		if len(args) > 0:
			try:
				args[0] = float(args[0])
				if len(args) == 1:
					guild = msg.guild
					od = await read('mi')

					od[guild.id] = args[0]
					await write('mi', od)
					await msg.channel.send('Mute increment has been set.')
					log_dict = await read('al')
					if guild.id in log_dict:

						disp_name = msg.author.display_name
						await log(
							f'`{disp_name}` set the mute increment to `{args[0]}`',
							msg
						)

				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} 5`'
					)
				elif not argTest(types, args):
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid arg types. Example command: `{command} 5`'
					)
			except IndexError:
						command = msg.content.lower().split(' ')[0]
						await msg.channel.send(
							f'Invalid arg types. Example command: `{command} 5`'
						)
		else:
			cd = (await read("mi"))[msg.guild.id]
			await msg.channel.send(f'The current mute increment is `{cd}`')


async def emoji_max(args, msg):
	try:
		args.remove('')
	except ValueError:
		print('oof', args)
	print(args)
	if msg.author.guild_permissions.administrator:
		if not len(args) == 0:
			try:
				try:
					args[0] = int(args[0])
					bad_args = False
				except ValueError:
					bad_args = True
					pass
				if len(args) == 1 and not bad_args:
					guild = msg.guild
					od = await read('em')

					od[guild.id] = args[0]
					await write('em', od)
					await msg.channel.send('Emoji max has been set.')
					log_dict = await read('al')
					if guild.id in log_dict:

						disp_name = msg.author.display_name
						await log(
							f'`{disp_name}` set the emoji max to `{args[0]}`',
							msg
						)

				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} 5`',
						msg
					)
				elif bad_args:
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid arg types. Example command: `{command} 5`',
						msg
					)
			except IndexError:
						command = msg.content.lower().split(' ')[0]
						await msg.channel.send(
							f'Invalid arg types. Example command: `{command} 5`'
						)
		else:
			cd = (await read("em"))[msg.guild.id]
			await msg.channel.send(f'The current emoji max is `{cd}`')


async def mention_limit(args, msg):
	try:
		args.remove('')
	except ValueError:
		print('oof', args)
	print(args)
	if msg.author.guild_permissions.administrator:
		if not len(args) == 0:
			try:
				try:
					args[0] = int(args[0])
					bad_args = False
				except ValueError:
					bad_args = True
					pass
				if len(args) == 1 and not bad_args:
					guild = msg.guild
					od = await read('ml')

					od[guild.id] = args[0]
					await write('ml', od)
					await msg.channel.send('Mention limit has been set.')
					log_dict = await read('al')
					if guild.id in log_dict:
						disp_name = msg.author.display_name
						await log(
							f'`{disp_name}` set the mention limit to `{args[0]}`',
							msg
						)

				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} 5`'
					)
				elif bad_args:
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid arg types. Example command: `{command} 5`'
					)
			except IndexError:
						command = msg.content.lower().split(' ')[0]
						await msg.channel.send(
							f'Invalid arg types. Example command: `{command} 5`'
						)
		else:
			cd = (await read("ml"))[msg.guild.id]
			await msg.channel.send(f'The current mention limit is `{cd}`')


async def action_channel(args, msg):
	try:
		args.remove('')
	except ValueError:
		print('oof', args)
	print(args)
	if msg.author.guild_permissions.administrator:
		if not len(args) == 0:
			try:
				try:
					args[0] = int(args[0][2:-1])
					bad_args = False
				except ValueError:
					bad_args = True
					pass
				if len(args) == 1 and not bad_args:
					guild = msg.guild
					od = await read('al')

					od[guild.id] = args[0]
					await write('al', od)
					await msg.channel.send('Action log channel has been set.')
					author = msg.author.display_name
					await log(
						f'`{author}` set the action log channel to <#{args[0]}>',
						msg
					)
				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} \#action-log`'
					)
				elif bad_args:
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} \#action-log`'
					)
			except IndexError:
						command = msg.content.lower().split(' ')[0]
						await msg.channel.send(
							f'Invalid ammount of args. Example command: `{command} \#action-log`'
						)
		else:
			cd = (await read("al"))[msg.guild.id]
			await msg.channel.send(f'The current action log channel is <#{cd}>')


async def mail_channel(args, msg):
	try:
		args.remove('')
	except ValueError:
		print('oof', args)
	print(args)
	if msg.author.guild_permissions.administrator:
		if not len(args) == 0:
			try:
				try:
					args[0] = int(args[0][2:-1])
					bad_args = False
				except ValueError:
					bad_args = True
					pass
				if len(args) == 1 and not bad_args:
					guild = msg.guild
					od = await read('mod_mail')

					od[guild.id] = args[0]
					await write('mod_mail', od)
					await msg.channel.send('Mod Mail channel has been set.')
					author = msg.author.display_name
					await log(
						f'`{author}` set the Mod Mail channel to <#{args[0]}>',
						msg
					)
				elif len(args) != 1:

					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} \#mod-mail`'
					)
				elif bad_args:
					command = msg.content.lower().split(' ')[0]
					await msg.channel.send(
						f'Invalid ammount of args. Example command: `{command} \#mod-mail`'
					)
			except IndexError:
						command = msg.content.lower().split(' ')[0]
						await msg.channel.send(
							f'Invalid ammount of args. Example command: `{command} \#mod-mail`'
						)
		else:
			cd = (await read("mod_mail"))[msg.guild.id]
			await msg.channel.send(f'The current mod mail channel is <#{cd}>')
