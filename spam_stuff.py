import datetime
from discord import NotFound
from role_find import get_muted_role
from commands.moderation_tools import findDate


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


def get_spam_chart():
	return spam_chart.read_cache('spamChart')


def log_offense(user, guild, duration, message):
	full_offense_dict = spam_chart.read_cache("spamChart")

	date = findDate(f"{str(duration)}s")

	if guild in full_offense_dict:
		guild_dict = full_offense_dict[guild]
	else:
		guild_dict = {}
	if user in guild_dict:
		user_dict = guild_dict[user]
	else:
		user_dict = []
	item = [user, message.id, guild, date]
	user_dict.append(item)
	guild_dict[user] = user_dict
	full_offense_dict[guild] = guild_dict
	spam_chart.cache("spamChart", full_offense_dict)

	return(len(user_dict))


async def check_expire(client):
	spamChart = get_spam_chart()
	del_list = []
	for a in spamChart:
		guild_chart = spamChart[a]
		for b in guild_chart:
			user_chart = guild_chart[b]
			for c in range(len(user_chart)):
				ok = user_chart[c]
				date = datetime.datetime.strptime(ok[3], "%Y-%m-%w-%W %H:%M:%S")
				if datetime.datetime.now() >= date:
					del_list.append(f'{a}/{b}/{c}')

	for a in del_list:
		a = a.split('/')

		stuff = spamChart[int(a[0])][int(a[1])][0]

		user = int(stuff[0])
		mid = stuff[1]
		guild = int(stuff[2])

		guild = await client.fetch_guild(int(guild))

		user = await guild.fetch_member(int(user))

		try:
			if (await get_muted_role(guild)) in user.roles:
				msg = await user.fetch_message(mid)
				await msg.delete()
		except NotFound:
			pass

		spamChart[int(a[0])][int(a[1])].remove(stuff)
		print('removed')

	spam_chart.cache('spamChart', spamChart)
