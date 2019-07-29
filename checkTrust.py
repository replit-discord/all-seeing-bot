import discord
from rw import read


async def checkRoles(guild, user):
	role_trust_dict = await read('td')
	if guild.id in role_trust_dict:
		user_roles = user.roles
		user_role_ids = [role.id for role in user_roles]
		guild_trust_roles = role_trust_dict[guild.id]
		if any(role in guild_trust_roles for role in user_role_ids):
			return True
		else:
			return False
	else:
		return False


async def checkUser(guild, user):
	user_trust_dict = await read('utd')
	if guild.id in user_trust_dict:
		if user.id in user_trust_dict[guild.id]:
			return True
		else:
			return False
	else:
		return False


async def checkTrust(guild, user):
	role = await checkRoles(guild, user)
	user = await checkUser(guild, user)
	if role or user:
		return True
	else:
		return False
