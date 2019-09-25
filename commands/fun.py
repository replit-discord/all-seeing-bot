import discord
import asyncio
from random import randint
helpText = '''
**`roll: <amount>d<sides>`** Gets the combined total of <amount> dice with <sides> sides.
'''
helpMsg = discord.Embed(
	title="Fun",
	description=helpText,
	color=0x00f2ff
)

helpMsg.set_footer(
	text='Comments or suggestions? Email feedback@allseeingbot.com '
	'for your suggestion to be heard'
)


async def roll(args, msg):
	channel = msg.channel
	if len(args) > 1:
		temp_msg = await msg.channel.send("Invalid ammount of arguments!")
		asyncio.sleep(2)
		await temp_msg.delete()
	else:
		data = args[0].split('d')
		ammount = int(data[0])
		dice_type = int(data[1])
		value = 0
		for a in range(ammount):
			value += randint(1, dice_type)

		embed = discord.Embed(
			title='**Results**',
			description=f'You rolled `{str(value)}`!',
			color=0xfffb00
		)
		embed.set_footer(
			text='Should I add a re-role option? '
			'Email feedback@allseeingbot.com to reply.'
		)
		await channel.send(embed=embed)


async def statroll(args, msg):
	channel = msg.channel
	author = msg.author

	while '' in args:
		args.remove('')

	if len(args) == 0:
		stats = []

		for n in range(6):
			results = []

			for l in range(4):
				results.append(randint(2, 6))

			results = sorted(results)
			results.remove(results[-1])
			value = 0
			for a in results:
				value += a
			print(value)


	else:
		await channel.send(f'<@{author.id}> this command takes no arguments')
