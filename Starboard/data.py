import os
from json_store_client import AsyncClient

client = AsyncClient(os.environ.get('JSON_LINK'))


class Storage:
	def __init__(self):
		self.data = {
			'star': {'None': 'None'},
			'msg': {'none': 'None'},
			'data': {'prefix': '.'},
			'leaders': {'None', 'None'}
		}

	async def init(self):
		value = await client.retrieve('data')
		self.data = value

	async def reset(self, guild):
		reset_value = {
			'star': {'None': 'None'},
			'msg': {'none': 'None'},
			'data': {
				'prefix': '.',
				'min': 2,
				'channels': ['None'],  # list of channels to be white/blacklisted
				'channel_on': False,  # True=whitelist False=blacklist
				'rchannels': ['None'],
				'rchannel_on': False
				# rchannels toggles whether or not the channel is listed for reactions
			},
			'leaders': {'None': 'None'}
		}
		fd = self.data
		fd[str(guild.id)] = reset_value
		await client.store('data', fd)

	def get_data(self, guild):
		return self.data[str(guild.id)]['data']

	def get_star(self, guild):
		return self.data[str(guild.id)]['star']

	def get_msg(self, guild):
		return self.data[str(guild.id)]['msg']

	def get_leaders(self, guild):
		return self.data[str(guild.id)]['leaders']

	async def set_leaders(self, guild, value):
		self.data[str(guild.id)]['leaders'] = value
		await client.store('data', self.data)

	async def set_data(self, guild, value):
		self.data[str(guild.id)]['data'] = value
		await client.store('data', self.data)

	async def set_msg(self, guild, value):
		self.data[str(guild.id)]['msg'] = value
		await client.store('data', self.data)

	async def set_star(self, guild, value):
		self.data[str(guild.id)]['star'] = value
		await client.store('data', self.data)


data = Storage()
