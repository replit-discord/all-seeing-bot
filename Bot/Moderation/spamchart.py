from tools.read_write import read, write
import discord
import datetime
import json
from discord import NotFound, Member
from utils import mute, find_date, get_muted_role


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
spam_chart.cache('spam_chart', {})


async def get_mute_duration(guild: discord.Guild) -> datetime.timedelta:
    data = await read('md')

    if guild.id in data:
        seconds = data[guild.id]
        print('ok')
        return datetime.timedelta(seconds=seconds)
    else:
        return datetime.timedelta(minutes=5)


def get_spam_chart():
    return spam_chart.read_cache('spam_chart')


def log_offense(message, duration):
    author = message.author
    if type(author) != Member:
        return
    full_offense_dict = spam_chart.read_cache("spam_chart")
    guild = message.guild
    timedelta = datetime.timedelta(seconds=int(duration))
    date = datetime.datetime.now() + timedelta

    if guild.id in full_offense_dict:
        guild_offenses = full_offense_dict[guild.id]
    else:
        guild_offenses = []

    item = (message, date)

    guild_offenses.append(item)

    full_offense_dict[guild.id] = guild_offenses
    spam_chart.cache("spam_chart", full_offense_dict)


async def check_expire():
    sc = get_spam_chart()
    new_data = {}
    now = datetime.datetime.now()
    for g in sc:
        data = sc[g]
        del_list = []
        for n in data:
            if n[1] < now:
                del_list.append(n)

        for d in del_list:
            data.remove(d)
            author = d[0].author
            muted = await get_muted_role(d[0].guild)
            if muted in author.roles:
                try:
                    await d[0].delete()
                except discord.NotFound:
                    pass
        new_data[g] = data
    spam_chart.cache('spam_chart', sc)


def check_user(user, limit):
    '''User needs to be a member object.'''
    spam_chart = get_spam_chart()
    guild = user.guild
    if guild.id in spam_chart:
        count = 0
        for a in spam_chart[guild.id]:
            if a[0].author.id == user.id:
                count += 1

        return count > limit
    else:
        return False


async def handle_message(message: discord.Message):
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
    log_offense(message, duration)

    if check_user(author, limit):
        if check_user(author, limit):
            duration = await get_mute_duration(author.guild)
            await spam_chart.cog.log(
                message,
                f'<@{author.id}> was automatically muted for {duration.seconds} seconds.',
                '**Automod**',
                color=0xff0000,
                showauth=True
            )
            await mute(author, duration)


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
    log_offense(message, duration)

    if check_user(author, limit):
        duration = await get_mute_duration(author.guild)
        await spam_chart.cog.log(
            message,
            f'<@{author.id}> was automatically muted for {duration.seconds} seconds.',
            '**Automod**',
            color=0xff0000,
            showauth=True
        )
        await mute(author, duration)


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
    log_offense(message, duration)

    if check_user(author, limit):
        duration = await get_mute_duration(author.guild)
        await spam_chart.cog.log(
            message,
            f'<@{author.id}> was automatically muted for {duration.seconds} seconds.',
            '**Automod**',
            color=0xff0000,
            showauth=True
        )
        await mute(author, duration)


def init(cog):
    spam_chart.cog = cog
