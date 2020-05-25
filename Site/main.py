from flask import Flask, render_template, request, session, redirect, jsonify, send_file
from oauth2_utils import make_session
import httpx
import os
import random
import asyncio
from utils import perm_check, handle_commands
from threading import Thread
from flask_wtf_stuff.manage import generate_command_field, generate_perm_field, CommandsForm
from encryption_tools import encode
import requests
import json
import os

key = os.environ.get('KEY')

BOT_SITE = os.environ.get('BOT_SITE')
SITE = os.environ.get('SITE')

request_client = httpx.AsyncClient()
inv_link = 'https://discordapp.com/oauth2/authorize?client_id=610205862090244106&scope=bot&permissions=402746566'
loop = asyncio.get_event_loop()

app = Flask(
    'AllSeeingBot',
    template_folder='templates',
    static_folder='static',
)

app.config.update(TEMPLATES_AUTO_RELOAD=True)

OAUTH2_CLIENT_SECRET = os.environ['CLIENT_TOKEN']
API_BASE_URL = 'https://discordapp.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'

TOKEN_URL = API_BASE_URL + '/oauth2/token'

TOKEN = requests.get(
	"https://gen-token--allawesome497.repl.co",
	username="AllSeeingBot-Site",
	password="AAIsTheMostAwesome497"
)

app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET


@app.before_request
def force_https():
    if 'X-Forwarded-Proto' in request.headers:
        if request.headers['X-Forwarded-Proto'] == 'http':
            return redirect(request.url.replace('http://', 'https://'))


@app.route('/')
def home():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    logged_in = not 'message' in user
    # if 'message' in user:
    # 	return redirect('/login')
    # return jsonify(
    # 	user=user,
    # 	guilds=guilds
    # )

    return render_template(
        'home.html',
        logged_in=logged_in,
        guilds=guilds,
        user=user,
        check=perm_check)


@app.route('/css/<file_name>')
def css(file_name):
    return send_file(f'static/css/{file_name}')


@app.route('/login')
def login():
    scope = request.args.get('scope', 'identify guilds')
    discord = make_session(
        scope=scope.split(' '),
        url=f'{SITE}/auth/callback')
    authorization_url, state = discord.authorization_url(
        AUTHORIZATION_BASE_URL)

    session['oauth2_state'] = state

    # print(state)
    return redirect(authorization_url)


@app.route('/auth/callback')
def callback():

    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url.replace('http://', 'https://'))
    session['oauth2_token'] = token

    return redirect('/')


def get_data(request_data, template_data):
    if 'c' in request.args:
        request_data['channel'] = request.args['c']

    if 'r' in request.args:
        request_data['role'] = request.args['r']

    if 'r' in request.args:
        template_data['role'] = request.args['r']
    else:
        template_data['role'] = None

    template_data['role_name'] = None
    return request_data, template_data


@app.route('/load/<guild_id>')
def load(guild_id):

    resp = requests.get(
        f'{BOT_SITE}/getinfo',
        data={'guild_id': guild_id})

    if 'message' in resp.json():
        return f'AllSeeingBot is not on this server. Click <a href="{inv_link}">here</a> to invite ASB.'

    info = resp.json()

    request_data = {'guild_id': guild_id}
    template_data = {
        'guild_id': guild_id,
        'channels': info['channels'],
        'roles': info['roles'],
    }

    if 'tab' in request.args:
        tab = request.args['tab']
        if tab == 'commands':
            is_perm = False
        else:
            is_perm = True
    else:
        is_perm = True
    print(request.args)
    request_data, template_data = get_data(request_data, template_data)

    for r in info['roles']:
        if str(r[1]) == template_data['role']:
            template_data['role_name'] = r[0]
            break

    if 'c' in request.args:
        template_data['channel'] = request.args['c']
    else:
        template_data['channel'] = None

    template_data['channel_name'] = None

    for c in info['channels']:
        if str(c[1]) == template_data['channel']:
            template_data['channel_name'] = c[0]
            break

    # print(is_perm, 'IS PERM')
    if is_perm:
        data = requests.get(
            f'{BOT_SITE}/getperms',
            data=request_data).json()

        perms = data['perms']

        # print(perms)
        template_data['form'] = generate_perm_field(perms)
        return render_template('perms.html', **template_data)
    else:

        resp = requests.get(
            f'{BOT_SITE}/getcommands',
            data=request_data)
        # print(resp)
        data = resp.json()
        commands = data['cogs']
        template_data['form'] = generate_command_field(commands)
        return render_template('commands.html', **template_data)


@app.route('/manage')
def root_manage():
    try:
        guild_id = session['GUILD_ID']
    except KeyError:
        return redirect('/')
    return redirect(f'/manage/{guild_id}')


@app.route('/manage/<guild_id>')
def manage(guild_id):
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    if 'message' in user:
        return redirect('/login')
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    guild_name = None

    for g in guilds:
        # print(g)
        if g['id'] == guild_id:
            guild_name = g['name']
            if not perm_check(g):
                return render_template('noperm.html', user=user)
    if not guild_name:
        return f'AllSeeingBot is not on this server. Click <a href="{inv_link}">here</a> to invite ASB.'
    session['GUILD_ID'] = guild_id

    if 'c' in request.args:
        channel = request.args['c']
    else:
        channel = None
    if 'r' in request.args:
        role = request.args['r']
    else:
        role = None
    print(request.args)
    return render_template(
        'manage.html',
        user=user,
        guild_id=guild_id,
        channel=channel,
        role=role,
        args=request.args,
        guild_name=guild_name)


@app.route('/submit', methods=["POST"])
def submit():

    if 'tab' in request.args:
        tab = request.args['tab']
        if tab == 'commands':
            is_perm = False
        else:
            is_perm = True
    else:
        is_perm = True
    # print(is_perm, 'IS PERM', request.args)
    if not is_perm:
        form = CommandsForm(request.form)
        if form.validate():
            return handle_commands()

        return jsonify(form=request.form, args=request.args)
    data = {}
    for a in request.form:
        if a.startswith('perms-'):
            data[a.split('-')[-1]] = True
    json_data = json.dumps(data)
    data_encoded = encode(key, json_data)
    guild_id = request.args['g']
    if 'GUILD_ID' not in session:
        return 'Nice try'
    if session['GUILD_ID'] != guild_id:
        return 'Nice try'
    print(data_encoded)
    request_data = {'data': data_encoded, 'guild': guild_id}
    if 'c' in request.args:
        request_data['channel'] = request.args['c']
    if 'r' in request.args:
        request_data['role'] = request.args['r']
    print('posting')
    resp = requests.post(
        f'{BOT_SITE}/submitperms',
        data=request_data,
		token=TOKEN,
    )
    print(resp)

    tab = 'perm'

    if 'c' in request.args:

        if 'r' in request.args:

            return redirect(
                f'/manage/{guild_id}?c={request.args["c"]}'
                f'&r={request.args["r"]}&tab={tab}'
            )
        return redirect(f'/manage/{guild_id}?c={request.args["c"]}&tab={tab}')

    if 'r' in request.args:
        return redirect(f'/manage/{guild_id}?r={request.args["r"]}&tab={tab}')

    return redirect(f'/manage/{guild_id}?tab={tab}')


def start_app():
    app.run(host='0.0.0.0', port=random.randint(2000, 9000))


if __name__ == '__main__':
    thread = Thread(target=start_app)
    thread.start()
    loop.run_forever()
