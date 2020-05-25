from flask import Flask, jsonify, request
from utils import get_checks, set_checks, check_raw_command, set_commands
from threading import Thread
import random
import json
import asyncio
import os
from encryption_tools import decode

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


blacklisted_cogs = [
    'dev',
    'moderation checks',
    'Logs'
]


key = os.environ.get('KEY')

app = Flask('')


@app.route('/')
def home():

    return '''<a href="https://discordbots.org/bot/610205862090244106" >
	<img src="https://discordbots.org/api/widget/610205862090244106.svg" alt="AllSeeingBot" />
</a>'''


def run():

    app.run(
        host='0.0.0.0',
        port=random.randint(2000, 9000)
    )


@app.route('/getcommands')
def get_commands():

    cogs = [cog for cog in bot.cogs.values(
    ) if cog.qualified_name not in blacklisted_cogs]
    data = {}
    ctx_data = request.form
    info = {}
    if 'channel_id' in request.form:
        info['channel_id'] = request.form['channel_id']
    if 'role_id' in request.form:
        guild = bot.get_guild(int(request.form['guild_id']))

        info['role'] = guild.get_role(int(request.form['role_id']))
    def_data = {}

    for cog in cogs:
        if cog.qualified_name in blacklisted_cogs:
            continue
        cog_data = [
            (
                cmd.name,
                check_raw_command(cmd, ctx_data, bot.loop, **info),
                cmd.short_doc
            ) for cmd in cog.get_commands()]

        data[cog.qualified_name] = cog_data
    return jsonify(
        cogs=data,
        synced=data == def_data
    )


@app.route('/getinfo')
def getchannels():
    guild_id = int(request.form['guild_id'])

    try:
        channels = []
        roles = []
        guild = bot.get_guild(guild_id)

        for c in guild.channels:

            if str(c.type) == 'text':
                channels.append((c.name, c.id))

            elif str(c.type) == 'category':
                channels.append((c.name, 'cat'))

        for r in guild.roles:

            roles.append((r.name, r.id))

        return jsonify(
            channels=channels,
            roles=roles
        )
    except AttributeError:
        return jsonify(message='failed')


class FakeRole:
    def __init__(self, id):
        self.id = int(id)


@app.route('/getperms')
def getperms():
    guild_id = request.form['guild_id']

    if 'channel' in request.form and 'role' in request.form:

        perms = asyncio.run_coroutine_threadsafe(
            get_checks(
                guild_id,
                request.form['channel'],
                [None, FakeRole(request.form['role'])]
            ),
            bot.loop
        )
        perms = perms.result()
        return jsonify(perms=perms)
    elif 'channel' in request.form:
        channel_id = request.form['channel']
        perms = asyncio.run_coroutine_threadsafe(
            get_checks(
                guild_id,
                channel_id
            ),
            bot.loop
        )
        perms = perms.result()

        return jsonify(perms=perms)
    elif 'role' in request.form:
        perms = asyncio.run_coroutine_threadsafe(
            get_checks(
                guild_id,
                None,
                [None, FakeRole(request.form['role'])]
            ),
            bot.loop
        )
        perms = perms.result()
        return jsonify(perms=perms)

    guild_perms = asyncio.run_coroutine_threadsafe(
        get_checks(int(guild_id)),
        bot.loop
    )
    perms = guild_perms.result()
    return jsonify(perms=perms)


@app.route('/submitperms', methods=['POST'])
def submitperms():
    print('got a request')
    data_raw = request.form['data']

    json_data = decode(key, data_raw)
    guild = request.form['guild']
    data = json.loads(json_data)
    role = None
    channel = None
    if 'role' in request.form:
        role = request.form['role']
    if 'channel' in request.form:
        channel = request.form['channel']
    asyncio.run_coroutine_threadsafe(
        set_checks(data, int(guild), channel, role),
        bot.loop
    ).result()
    return 'done'


@app.route('/submitcommands', methods=["POST"])
def submitcommands():
    data_raw = request.form['data']

    json_data = decode(key, data_raw)
    data = json.loads(json_data)

    cogs = [cog for cog in bot.cogs.values(
    ) if cog.qualified_name not in blacklisted_cogs]
    commands = []
    for cog in cogs:
        for command in cog.get_commands():
            commands.append(command.name)
    guild = request.form['guild']
    print(request.form)
    if 'channel' in request.form:
        channel = request.form['channel']
    else:
        channel = None
    if 'role' in request.form:

        role = request.form['role']
    else:
        role = None
    print('ROLE', role)

    asyncio.run_coroutine_threadsafe(
        set_commands(bot, data, guild, channel, role),
        bot.loop
    ).result()
    return 'done'



def keep_alive(d_bot):
    global bot
    bot = d_bot

    t = Thread(target=run)
    t.start()
