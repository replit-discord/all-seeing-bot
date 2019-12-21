import discord
import asyncio
from math import ceil
from discord.ext import commands

from tools.read_write import read, write
from utils import get_muted_role, find_date, InvalidDate
from random import randint


class Fun(commands.Cog, name='Fun'):
	'''Fun commands'''

	def __init__(self, bot):
		self.bot = bot
		self.color = 0xdb07bf

	def cog_check(self, ctx):
		author = ctx.author
		if not author.guild_permissions.administrator:
			return True
		return True

			# cmd_name = ctx.command.name
			# return check_trust(cmd_name, author)

	@commands.command(name='roll')
	async def roll(self, ctx, dice: str = 'd6', *argv):
		'''Roll dice.
		```css
		Example Usage:
		``````css
		?roll 5  Roll 5 six sided dice.```
		```css
		?roll 5d10  // Roll 5 ten sided dice.```
		```css
		?roll 5 -s  // Roll 5 six sided dice and show each roll.```
		```css
		?roll 5d10 -s // Roll 5 ten sided dice and show each roll.```
		'''

		if 'd' in dice:
			listed_dice = dice.split('d')
			ammount = int(listed_dice[0])
			sides = int(listed_dice[1])
		else:
			ammount = int(dice)
			sides = 6
		rolls = []
		total = 0
		for roll in range(ammount):
			roll_ammount = randint(1, sides)
			rolls.append(roll_ammount)
			total += roll_ammount
		max_score = ammount * sides
		low_score = ceil(.1 * max_score) / max_score
		# low_score += ammount - 1
		# print(low_score, ammount)
		high_score = ceil(.9 * max_score) / max_score
		print(sides * ammount, max_score)
		percent = total / max_score
		print(percent, total)
		user = ctx.author
		print(percent, low_score, high_score)
		if percent >= high_score:
			desc = f'🎉 <@{user.id}>, you rolled {total}! 🎉'
		elif percent <= low_score:

			desc = f'😬 <@{user.id}>, you rolled {total}. 😬'
		else:
			desc = f'<@{user.id}>, you rolled {total}.'
		if argv is not []:
			if '-s' in argv:
				numbered_list = [
					f'#{num+1}: {rolls[num]}' for num in range(len(rolls))
				]
				results = '\n'.join(numbered_list)
				desc += '\n'

				if len(results) <= 100:
					desc += '```css\n'
					desc += results
					desc += '```'

				else:
					desc += (
						'The results were too long to'
						' add to this message. 😔'
					)

		await ctx.send(desc)

	@commands.command(name='coinflip', aliases=['flip'])
	async def coin_flip(self, ctx, ammount: int = 1):
		'''Flip a Coin
		```css
		Example Usage:
		``````css
		?coinflip // Flips a single coin
		``````css
		?flip 5 // Flips five coins.
		```
		'''
		def flip():
			heads = randint(0, 1) == 1  # Returns true if heads
			if heads:
				return 'Heads'
			else:
				return 'Tails'

		if ammount == 1:
			desc = f'You got __{flip()}__!'

		elif ammount <= 20:

			desc = 'Results: ```css\n'

			for n in range(ammount):
				desc += f'#{n+1}: {flip()}\n'

			desc += '```'

		else:
			desc = "**Can't flip more then 20 coins at a time!!!**"

		await ctx.send(desc)


def setup(bot):
	bot.add_cog(Fun(bot))
