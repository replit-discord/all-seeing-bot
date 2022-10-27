import re
import json
import asyncio
import discord
from collections import abc
from defualts import command_defaults
from Moderation.Message_Checks import checks
from datetime import timedelta, datetime
from tools.read_write import read, write
from pygments import highlight, lexers, formatters


dev_ids = [
    487258918465306634,
    527937324865290260
]

special_commands = [
    'write', 'read',
    'exec', 'reload',
    'load', 'unload',
    'listextensions', 'le',
    'helper',
]


def update(old, new, output=True):

    for k, v in new.items():
        if isinstance(v, abc.Mapping):
            old[k] = update(old.get(k, {}), v, False)
        else:
            old[k] = v

    return old


checks_mapped = {c.name: c.check_name for c in checks}


class LazyChannel:
    def __init__(self, channel_id):
        self.id = channel_id


class LazyGuild:
    def __init__(self, guild_id):
        self.id = int(guild_id)


class LazyAuthor:
    id = -1
    guild = None
    guild_permissions = discord.Permissions(0)
    roles = ['none']


class LazyCtx:
    def __init__(self, command, **info):
        self.command = command
        self.guild = LazyGuild(info['guild_id'])
        self.author = LazyAuthor()
        # open('bruh.txt', 'w').write(open('bruh.txt', 'r').read() + '\n\n\n' + str(info))
        if 'role' in info:
            self.author.roles = [info['role']]
            self.author.guild_permissions = info['role'].permissions

        else:
            self.author.roles = []
        if 'channel' in info:
            self.channel = LazyChannel(info['channel'])
        else:
            self.channel = None


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


def index_args(args):
    indexed = [[]]

    for arg in args:
        if not arg.startswith('-'):
            indexed[-1].append(arg)
        else:
            indexed.append([arg])
    return indexed


class InvalidDate(BaseException):
    pass


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


async def get_muted_role(guild) -> discord.Role:
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


async def mute(user: discord.Member, duration: timedelta):
    end_date = datetime.now() + duration

    try:
        muted = await get_muted_role(user.guild)
        await user.add_roles(muted, reason="automod")

        data = {
            str(user.guild.id): {str(user.id): end_date.strftime("%Y-%m-%w-%W %H:%M:%S")}
        }
        muted = await read('muteList')

        muted = update(muted, data)
        await write('muteList', muted)

    except discord.Forbidden:
        pass


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


class PermCache:
    _data = {}

    @property
    def data(self):
        return self._data

    def get_data(self, user_id, guild_id, channel):
        data = self.data
        if not channel:
            chan_id = 'general'
        else:
            chan_id = channel.id
        if not guild_id in data:
            return None

        if not user_id in data[guild_id]:
            return None
        if not chan_id in data[guild_id][user_id]:
            return None
        return data[guild_id][user_id][chan_id]

    def set_data(self, user_id, guild_id, channel, new_data):
        if not channel:
            chan_id = 'general'
        else:
            chan_id = channel.id
        data = self.data
        if not guild_id in data:
            self._data[guild_id] = {user_id: {chan_id: new_data}}
        else:
            self._data[guild_id][user_id] = {chan_id: new_data}

    def reset(self, guild_id):
        data = self.data
        if guild_id in data:
            del self._data[guild_id]

    def reset_user(self, user):
        data = self.data
        guild = user.guild
        if guild.id in data:
            if user.id in data[guild.id]:

                del self._data[guild.id][user.id]


perm_cache = PermCache()


async def get_checks(
        guild_id,
        channel_id=None,
        roles=None,
        as_dict=False
):
    perms = await read('perms')
    if str(guild_id) in perms:
        guild_perms = perms[str(guild_id)]
    else:
        guild_perms = {}

    if 'checks' in guild_perms:
        guild_checks = guild_perms['checks']
    else:
        guild_checks = {
            'general': {},
            'roles': {},
            'channels': {},
        }
    all_roles = guild_checks['roles']
    check_data = {c.name: c.default for c in checks}
    if 'general' in guild_checks:
        check_data = update(check_data, guild_checks['general'])

    role_and_channel = False

    if roles:
        for role in roles[1:][::-1]:

            if str(role.id) in all_roles:
                role_checks = all_roles[str(role.id)]
            else:
                continue

            if channel_id and str(channel_id) in role_checks:
                check_data = update(check_data, role_checks[str(channel_id)])
                role_and_channel = True
                break
            elif 'general' in role_checks:
                check_data = update(check_data, role_checks['general'])
                break

    if not role_and_channel:
        if channel_id and str(channel_id) in guild_checks['channels']:
            check_data = update(
                check_data, guild_checks['channels'][str(channel_id)])
    if as_dict:
        return check_data
    return_data = []
    for c in check_data:
        return_data.append((checks_mapped[c], check_data[c], c))

    return return_data


async def set_checks(data, guild_id, channel_id=None, role_id=None):

    perms = await read('perms')
    check_data = {
        c: False for c in [
            check.name for check in checks
        ]
    }
    check_data = update(check_data, data, False)

    if str(guild_id) in perms:
        guild_perms = perms[str(guild_id)]
    else:
        guild_perms = {}

    if 'checks' not in guild_perms:
        guild_checks = {
            'roles': {},
            'channels': {},
            'general': {}
        }
    else:
        guild_checks = guild_perms['checks']

    if role_id and channel_id:

        updated = {
            'roles': {
                str(role_id): {str(channel_id): check_data}
            }
        }
    elif role_id:
        updated = {
            'roles': {
                str(role_id): {'general': check_data}
            }
        }
    elif channel_id:
        updated = {
            'channels': {
                str(channel_id): check_data
            }
        }
    else:
        updated = {
            'general': check_data
        }

    guild_checks = update(guild_checks, updated)
    if str(guild_id) in perms:

        perms[str(guild_id)]['checks'] = guild_checks
    else:
        perms[str(guild_id)] = {'checks': guild_checks}

    await write('perms', perms)


async def set_command(
        command,
        enabled,
        guild_id,
        role_id=None,
        channel_id=None,
        perms=None
):
    if not perms:
        perms = await read('perms')
        write_perms = True
    else:
        write_perms = False
    perm_cache.reset(int(guild_id))
    if str(guild_id) in perms:
        guild_perms = perms[guild_id]
    else:
        guild_perms = {}
    if 'commands' in guild_perms:
        command_perms = guild_perms['commands']
    else:
        command_perms = {
            'general': {},
            'roles': {},
            'channels': {},
        }
    if role_id:
        if 'roles' in command_perms:
            all_roles = command_perms['roles']
            if str(role_id) in all_roles:
                role_commands = all_roles[str(role_id)]
            else:
                role_commands = {}
        else:
            all_roles = {}
            role_commands = {}

        if channel_id:
            if 'channels' in role_commands:
                chan_commands = command_perms['channels']
                if channel_id in chan_commands:

                    chan_commands[channel_id][command] = enabled
                else:
                    chan_commands[channel_id] = {command: enabled}
            else:
                chan_commands = {channel_id: {command: enabled}}
            role_commands['channels'] = chan_commands
        else:
            if 'general' in role_commands:
                general_commands = role_commands['general']
                general_commands[command] = enabled
            else:
                general_commands = {command: enabled}

            role_commands['general'] = general_commands
        all_roles[role_id] = role_commands
        command_perms['roles'] = all_roles
    elif channel_id:
        if 'channels' in command_perms:
            chan_commands = command_perms['channels']
        else:
            chan_commands = {}
        if channel_id in chan_commands:
            chan_commands[channel_id][command] = enabled
        else:
            chan_commands[channel_id] = {command: enabled}

        command_perms['channels'] = chan_commands
    else:
        if 'general' in command_perms:
            general_commands = command_perms['general']
            general_commands[command] = enabled
        else:

            general_commands = {command: enabled}

        command_perms['general'] = general_commands
    guild_perms['commands'] = command_perms
    perms[str(guild_id)] = guild_perms

    if write_perms:
        await write('perms', perms)
    return perms


async def set_commands(
        bot,
        data,
        guild_id,
        channel_id=None,
        role_id=None
):

    perms = await read('perms')

    c_perms = {cmd.name: False for cmd in bot.commands}
    for c in data:
        c_perms[c] = True

    for c in c_perms:
        perms = update(perms, await set_command(
            c,
            c_perms[c],
            guild_id,
            role_id,
            channel_id,
            perms
        ))

    await write('perms', perms)


def check_type(user):
    try:
        user.guild  # Will throw an AttributeError if its a user
        return True
    except AttributeError:
        return False


async def check_command(ctx):

    if ctx.command.name in special_commands:
        print("returning yes for", ctx.command.name)
        return True  # Devs (so me) can always use dev commands
    if not check_type(ctx.author):
        if ctx.command.name in command_defaults:
            return command_defaults[ctx.command.name] == 0
        return False
    if ctx.author.guild_permissions.administrator:
        return True

    data = perm_cache.get_data(ctx.author.id, ctx.guild.id, ctx.channel)
    if data != None:
        if ctx.command.name not in data:
            return True
        return data[ctx.command.name]

    command = ctx.command.name

    perms = {}
    for cmd in command_defaults:

        cmd_perms = discord.Permissions(command_defaults[cmd])
        if cmd_perms.value == 0:
            perms[cmd] = True
            continue

        if ctx.author.guild_permissions.value == 0:
            perms[cmd] = False
            continue

        perms[
            cmd
        ] = ctx.author.guild_permissions.is_superset(
            cmd_perms
        )

    perm_data = await read('perms')

    if str(ctx.guild.id) in perm_data:
        guild_perms = perm_data[str(ctx.guild.id)]
    else:
        guild_perms = {}
    if 'commands' in guild_perms:
        command_perms = guild_perms['commands']
    else:

        command_perms = {
            'general': {},
            'roles': {},
            'channels': {},
        }

    channel = ctx.channel
    roles = ctx.author.roles

    perms = update(perms, command_perms['general'])
    if 'channels' in command_perms:
        channel_perms = command_perms['channels']
    else:
        channel_perms = {}

    if 'roles' in command_perms:
        role_perms = command_perms['roles']
    else:
        role_perms = {}

    if channel != None and str(channel.id) in channel_perms:

        perms.update(channel_perms[str(channel.id)])

    for role in roles:
        if str(role.id) in role_perms:
            r_perms = role_perms[str(role.id)]
            if 'general' in r_perms:
                perms.update(r_perms['general'])

            if channel != None and str(channel.id) in r_perms:
                perms.update(r_perms[str(channel.id)])

    if command not in perms:
        perms[command] = False
    if ctx.author.id != -1:
        perm_cache.set_data(ctx.author.id, ctx.guild.id, channel, perms)

    return perms[command]


def check_raw_command(command, data, loop, **info):

    # open()

    ctx = LazyCtx(command, **info)

    return asyncio.run_coroutine_threadsafe(
        check_command(ctx),
        loop
    ).result()

