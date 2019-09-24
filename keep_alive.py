from flask import Flask
from threading import Thread
import random

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


def keep_alive():
	# print('>keep_alive')
	t = Thread(target=run)
	t.start()
