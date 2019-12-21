import re
import discord
from datetime import timedelta, datetime
from tools.read_write import read, write


dev_ids = [
	487258918465306634,
	527937324865290260,
	534218348830130177
]


def is_dev(ctx):
	author = ctx.author
	return author.id in dev_ids


def execute(_code, loc):
	'''
	Executes code asynchronously, credits to mat, https://matdoes.dev
	'''
	_code = _code.replace('\n', '\n ')
	globs = globals()
	globs.update(loc)
	exec(
		'async def __ex():\n ' + _code,
		globs
	)
	return globs['__ex']()


async def check_allowed(ctx):
	pass


def index_args(args):
	indexed = [[]]

	for arg in args:
		if not arg.startswith('-'):
			indexed[-1].append(arg)
		else:
			indexed.append([arg])
	return indexed


class InvalidDate(BaseException): pass


def find_date(string):  # Credits to @mat1 for this
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
	return total_time


async def get_muted_role(guild):
	muted_role = discord.utils.get(guild.roles, name='Muted')
	if muted_role is None:
		full_mute_role_list = await read('mri')
		if guild.id in full_mute_role_list:
			role = full_mute_role_list[guild.id]
			role = guild.get_role(role)
		muted_permissions = discord.Permissions()
		muted_permissions.send_messages = False
		muted_permissions.add_reactions = False
		muted_role = await guild.create_role(
			name='Muted',
			permissions=muted_permissions,
			color=discord.Color.dark_red()
		)

	return muted_role


async def error_log(tb, error, bot):
	error_type = str(error[0])[8:][:-2]
	if 'forbidden' not in error_type.lower():
		embed = discord.Embed(
			title=f'**{error_type}**',
			description=f'```py\n{tb}\n```',
			color=0xff0000
		)


		embed.timestamp = datetime.now()
		guild = bot.get_guild(585606083897458691)
		channel = guild.get_channel(626223737376604191)
		await channel.send(embed=embed)
