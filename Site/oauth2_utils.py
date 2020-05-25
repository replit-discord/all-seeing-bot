import os
from requests_oauthlib import OAuth2Session
from flask import session

OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['CLIENT_TOKEN']
OAUTH2_REDIRECT_URI = 'https://dev.allseeingbot.com/auth/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None, url=OAUTH2_REDIRECT_URI):
    '''print(
            OAUTH2_CLIENT_ID, '\n',
            token, '\n',
            state, '\n',
            scope, '\n',
            OAUTH2_REDIRECT_URI, '\n',
            {
                    'client_id': OAUTH2_CLIENT_ID,
                    'client_secret': OAUTH2_CLIENT_SECRET,
            }, '\n',
            TOKEN_URL, '\n',
            token_updater
    )'''
    print(url)
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=url,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)
