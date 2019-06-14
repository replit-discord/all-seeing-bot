from flask import Flask
from threading import Thread
from random import randint

app = Flask('')


@app.route('/')
def home():
    return 'Im in'


def run():
    app.run(host='0.0.0.0', port=randint(2000, 9000))


def keep_alive():
    t = Thread(target=run)
    t.start()
