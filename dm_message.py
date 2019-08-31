import discord
import datetime
from rw import read, write


async def mod_mail(message, client):
	user = message.author
	channel = message.channel

	guild_list = []
	print(channel.type)
	for m in client.guilds:

		if user.id in [y.id for y in m.members]:
			guild_list.append([m.id, m])

	if len(guild_list) > 1:
		guild_numbers = {}
		for ng in range(len(guild_list)):
			name = guild_list[ng][1].name
			guild_numbers[ng] = [name, guild_list[ng][1]]
		fancy_text = '\n'
		for number in guild_numbers:
			fancy_text += f'{str(number + 1)}: `{guild_numbers[number][0]}`\n\n'
		content = message.content
		if content.startswith('?mail'):
			content = content.split(' ')
			msg = ' '.join(content[2:])
			if int(content[1]) - 1 in guild_numbers:
				content[1] = int(content[1]) - 1
				print(guild_numbers)
				print(guild_numbers[content[1]])
				guild = guild_numbers[content[1]][1]
			else:
				content = f'That guild is not in your list!. \nYour list of guilds is: \n{fancy_text}'
				embed = discord.Embed(
					title="Guilds",
					description=content,
					color=0xff00dd
				)
				await channel.send(embed=embed)

		else:

			content = f'''
You are in multiple guilds with the ASB bot. Please use `?mail <guild number> <message>` to send your message.
The numbers for your guilds are:
{fancy_text}
'''

			embed = discord.Embed(
				title="Guilds",
				description=content,
				color=0xff00dd
			)
			await channel.send(embed=embed)
	else:
		msg = message.content
		guild = guild_list[0][1]
	try:
		full_mod_mail = await read('mod_mail')
		print(full_mod_mail)
		if guild.id in full_mod_mail:
			channel_id = full_mod_mail[guild.id]
			log_channel = discord.utils.get(guild.text_channels, id=channel_id)
			embed = discord.Embed(
				title=str(user),
				color=0x52fc03
			)
			embed.add_field(name='**Mod Mail**', value=f'{msg}')
			time = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
			embed.set_footer(text=time)
			await log_channel.send(embed=embed)
			await channel.send('Your message has been recieved')
		else:
			await channel.send('That guild does not have mod mail setup!.')
	except UnboundLocalError:
		pass
