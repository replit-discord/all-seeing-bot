import discord
from commands import data_tweaking
from commands import moderation_tools
from checkTrust import checkTrust
main_help = discord.Embed(
	title='Help',
	description='''
**Currently, I do not have any commands for non-moderators.  I appologize inconvenience **''')
main_help.set_footer(
	text='Use help <catagory> to get help on a certain section.'
)
mod_help = discord.Embed(title='Help', description='''
**Customization:** Customization commands, such as mute duration
**Moderation:** Moderation commands.''', color=0xff8000)
mod_help.set_footer(
	text='Use help <catagory> to get help on a certain section.'
)
mod_pgs = {
	'customization': data_tweaking.helpMsg,
	'moderation': moderation_tools.helpMsg
}

trust_moderation_help = discord.Embed(
	title='Moderation',
	description='''
**`kick <user> <reason*>`:**   Kick a user.

**`mute <user> <time*> <reason*>`:**   Mute a user for a period of time.

**`unmute <user> <reason*>`:**   Unmute a user.

**`warn <user> <reason>`:**   Warn a user.

(*=optional)''',
	color=0xd82222
)
trust_pgs = {
	'moderation': trust_moderation_help
}
trust_help = '**Moderation:** Moderation commands.'
trust_help = discord.Embed(
	title='Help',
	description=trust_help,
	color=0xff8000
)
mainPgs = {}


async def Help(args, msg):
	print(msg.author.guild_permissions.administrator)
	if '' in args:
		args.remove('')
	channel = msg.channel
	if msg.author.guild_permissions.administrator:
		if len(args) == 0:
			await channel.send(embed=mod_help)
		elif len(args) == 1:
			if args[0].lower() in mod_pgs:
				await channel.send(embed=mod_pgs[args[0].lower()])
			else:
				await channel.send(args[0].lower() + ' is not in the help list.')
		else:
			await channel.send(
				'Invalid ammount of args. example command: `help Customization`'
			)

	elif (await checkTrust(msg.guild, msg.author)):
		if len(args) == 0:
			await channel.send(embed=trust_help)
		elif len(args) == 1:
			if args[0].lower() in trust_pgs:
				await channel.send(embed=trust_pgs[args[0].lower()])
			else:
				await channel.send(args[0].lower() + ' is not in the help list.')
		else:
			await channel.send(
				'Invalid ammount of args. example command: `help Customization`'
			)

	else:
		if len(args) == 0:
			await channel.send(embed=main_help)
		elif len(args) == 1:
			if args[0].lower() in mainPgs:
				await channel.send(embed=mainPgs[args[0].lower()])
			else:
				await channel.send(args[0].lower() + ' is not in the help list.')
		else:
			await channel.send(
				'Invalid ammount of args. example command: `help Customization`'
			)
