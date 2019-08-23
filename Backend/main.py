import asyncio
import ast
import datetime
import keep_alive
from encryption_tools import encode, decode
import os
import motor.motor_asyncio

mongo_link = os.getenv('mlab_link') + '?retryWrites=false'
client = motor.motor_asyncio.AsyncIOMotorClient(mongo_link)
db = client.asb_dev
main_collection = db.main_collection\

key = os.environ.get('KEY')


async def read(src, lEval=True, decrypt=True):

	if decrypt:
		try:
			data = decode(key, ((await main_collection.find_one({"_id": src}))['data']))
		except AttributeError:
			data = decode(key, await client.retrieve(src))
		if lEval:
			value = ast.literal_eval(data)
		else:
			value = str(data)
		return value
	else:
		data = await client.retrieve(src)

		if lEval:
			value = ast.literal_eval(data)
		else:
			value = str(data)
		return value


async def write(src, value, encrypt=True):
	if encrypt:
		await main_collection.update_one({"_id": src}, {"$set": {"data": str(encode(key, str(value)))}})
	else:
		await main_collection.update_one({"_id": src}, {"$set": {"data": str(value)}})

async def check_expire():
	spam_chart = await read('spamChart')
	del_list = []
	for a in spam_chart:
		guild_chart = spam_chart[a]
		for b in guild_chart:
			user_chart = guild_chart[b]
			for c in user_chart:
				date = datetime.datetime.strptime(c, "%Y-%m-%w-%W %H:%M:%S")
				if datetime.datetime.now() >= date:
					del_list.append(f'{a}/{b}/{c}')
	for a in del_list:
		a = a.split('/')
		print('removing')
		spam_chart[int(a[0])][int(a[1])].remove(a[2])
		print('removed')
	
	await write('spamChart', spam_chart)

async def main_loop():
	print("Loop Started")
	while True:
		await check_expire()
		await asyncio.sleep(1)


loop = asyncio.get_event_loop()
keep_alive.keep_alive()
loop.run_until_complete(main_loop())
