from flask import redirect, jsonify, request
from perms import Permissions
from encryption_tools import encode
import requests
import os
import json

key = os.environ.get('KEY')


def perm_check(guild):
    return Permissions(guild['permissions']).administrator


def handle_commands():
    guild_id = request.args['g']
    commands = []

    for n in request.form:

        if n.startswith('command-'):
            commands.append(n.split('-')[-1])
    data = {c: True for c in commands}
    data_encoded = encode(key, json.dumps(data))
    request_data = {'data': data_encoded, 'guild': guild_id}
    if 'r' in request.args:
        request_data['role'] = request.args['r']
    if 'c' in request.args:
        request_data['channel'] = request.args['c']
    print(request_data)
    res = requests.post(
        'https://AllSeeingBot-DEV.allawesome497.repl.co/submitcommands',
        data=request_data)
    print("GOT A RESPONSE", res)
    tab = 'commands'
    if 'c' in request.args:

        if 'r' in request.args:

            return redirect(f'/manage/{guild_id}?c={request.args["c"]}'
                            f'&r={request.args["r"]}&tab={tab}')
        return redirect(f'/manage/{guild_id}?c={request.args["c"]}&tab={tab}')

    if 'r' in request.args:
        return redirect(f'/manage/{guild_id}?r={request.args["r"]}&tab={tab}')

    return redirect(f'/manage/{guild_id}?tab={tab}')
