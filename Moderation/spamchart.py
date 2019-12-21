from tools.read_write import read, write

import datetime
from discord import NotFound
from utils import get_muted_role, find_date



class data:
	class spam_chart:
		def __init__(self):
			self.data = {}

		def cache(self, key, data):
			'''Add data to cache'''
			self.data[key] = data

		def read_cache(self, key):
			cache = self.data
			if key in cache:
				return cache[key]

		def check_cache(self, key):
			cache = self.data
			return key in cache


spam_chart = data.spam_chart()
spam_chart.cache('spamChart', {})
spam_chart.cache('after_spam', {})


def get_spam_chart():
	return spam_chart.read_cache('spamChart')


def log_offense(author, guild, duration, message):
	full_offense_dict = spam_chart.read_cache("spamChart")
	guild_id = guild.id
	user = author.id
	timedelta = find_date(f"{str(duration)}s")
	date = datetime.datetime.now() + timedelta
	date = date.strftime("%Y-%m-%w-%W %H:%M:%S")
	if guild_id in full_offense_dict:
		guild_dict = full_offense_dict[guild.id]
	else:
		guild_dict = {}
	if user in guild_dict:
		user_dict = guild_dict[user]
	else:
		user_dict = []
	item = [author, message, guild, date]
	user_dict.append(item)
	guild_dict[user] = user_dict
	full_offense_dict[guild_id] = guild_dict
	spam_chart.cache("spamChart", full_offense_dict)

	return(len(user_dict))


async def check_expire():
	spamChart = get_spam_chart()
	del_list = []
	for a in spamChart:
		guild_chart = spamChart[a]
		for b in guild_chart:
			user_chart = guild_chart[b]

			for c in range(len(user_chart)):
				try:
					ok = user_chart[c]
					date = datetime.datetime.strptime(ok[3], "%Y-%m-%w-%W %H:%M:%S")
					if datetime.datetime.now() >= date:
						if len(user_chart) > 1:
							await handle_infractions(ok[2], ['w'])
					
						del_list.append(f'{a}/{b}/{c}')
				except Exception:
					del_list.append(f'{a}/{b}/{c}')

	for a in del_list:
		a = a.split('/')

		stuff = spamChart[int(a[0])][int(a[1])][0]
		guild = stuff[2]
		user = stuff[0]
		msg = stuff[1]

		try:

			if (await get_muted_role(guild)) in user.roles:

				await msg.delete()

		except NotFound:
			pass

		spamChart[int(a[0])][int(a[1])].remove(stuff)

	spam_chart.cache('spamChart', spamChart)


def check_user(user, limit):
	'''User needs to be a member object.'''
	spam_chart = get_spam_chart()
	guild = user.guild
	if guild.id in spam_chart:
		guild_spam_chart = spam_chart[guild.id]
		if user.id in guild_spam_chart:
			if len(guild_spam_chart[user.id]) >= limit:
				return True
			else:
				return False
		else:
			return False
	else:
		return False


async def handle_message(message):
	author = message.author
	guild = message.guild
	full_duration_dict = await read('od')

	if guild.id in full_duration_dict:
		duration = full_duration_dict[guild.id]
	else:
		duration = 5
		full_duration_dict[guild.id] = 5
		await write('od', full_duration_dict)

	full_limit_dict = await read('ol')

	if guild.id in full_limit_dict:
		limit = full_limit_dict[guild.id]

	else:
		limit = 5
		full_limit_dict[guild.id] = 5
		await write('ol', full_limit_dict)

	if guild.id in full_limit_dict:
		limit = full_limit_dict[guild.id]

	else:
		limit = 5
	log_offense(author, guild, duration, message)

	return check_user(author, limit)


async def handle_infractions(message, failed_checks):
	author = message.author
	guild = message.guild
	full_duration_dict = await read('od')

	if guild.id in full_duration_dict:
		duration = full_duration_dict[guild.id]
	else:
		duration = 5
		full_duration_dict[guild.id] = 5
		await write('od', full_duration_dict)

	duration = (len(failed_checks) + 1) * duration

	full_limit_dict = await read('ol')

	if guild.id in full_limit_dict:
		limit = full_limit_dict[guild.id]

	else:
		limit = 5
		full_limit_dict[guild.id] = 5
		await write('ol', full_limit_dict)
	log_offense(author, guild, duration, message)

	return check_user(author, limit)


async def handle_banned_emoji(reaction, user):
	message = reaction.message
	author = user
	guild = message.guild
	full_duration_dict = await read('od')

	if guild.id in full_duration_dict:
		duration = full_duration_dict[guild.id]
	else:
		duration = 5
		full_duration_dict[guild.id] = 5
		await write('od', full_duration_dict)

	full_limit_dict = await read('ol')

	if guild.id in full_limit_dict:
		limit = full_limit_dict[guild.id]

	else:
		limit = 5
		full_limit_dict[guild.id] = 5
		await write('ol', full_limit_dict)

	if guild.id in full_limit_dict:
		limit = full_limit_dict[duration]

	else:
		limit = 5
	log_offense(author, guild, duration, message)

	return check_user(author, limit)
