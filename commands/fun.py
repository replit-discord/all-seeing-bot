import discord
import asyncio
from random import randint
help_message = '''
**`roll: <amount>d<sides>`** Gets the combined total of <amount> dice with <sides> sides.



'''


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
