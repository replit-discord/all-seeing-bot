import re
import discord
from datetime import datetime, timedelta


class InvalidDate(BaseException): pass


def find_date(string):  # Credits to mat for this script again
	times = {
		'months': timedelta(days=30),
		'month': timedelta(days=30),
		'mo': timedelta(days=30),

		'weeks': timedelta(weeks=1),
		'week': timedelta(weeks=1),
		'w': timedelta(weeks=1),

		'days': timedelta(days=1),
		'day': timedelta(days=1),
		'd': timedelta(days=1),

		'hours': timedelta(hours=1),
		'hour': timedelta(hours=1),
		'h': timedelta(hours=1),

		'minutes': timedelta(minutes=1),
		'minute': timedelta(minutes=1),
		'm': timedelta(minutes=1),

		'seconds': timedelta(seconds=1),
		'second': timedelta(seconds=1),
		's': timedelta(seconds=1),
	}
	leftover_string = string
	total_time = timedelta()
	while leftover_string:
		found_match = None
		found_time = None
		for t in times:
			matched = re.match(r'^(\d+) ?' + t, leftover_string)
			if matched is not None:
				found_match = matched
				found_time = times[t]
				break
		if found_match is None:
			raise InvalidDate(f'Invalid date "{string}"')
		amount = matched.group(1)
		added_time = found_time * int(amount)
		total_time += added_time

		string_end = found_match.span()[1]

		leftover_string = leftover_string[string_end:]
		leftover_string = leftover_string.strip()
	return str((datetime.now() + total_time).strftime('%Y-%m-%w-%W %H:%M:%S'))


async def error_log(tb, error, client):
	error_type = str(error[0])[8:][:-2]

	embed = discord.Embed(
		title=f'**{error_type}**',
		description=f'```py\n{tb}\n```',
		color=0xff0000
	)

	embed.set_footer(text=find_date('0s'))

	guild = client.get_guild(585606083897458691)
	channel = guild.get_channel(626223737376604191)
	await channel.send(embed=embed)
