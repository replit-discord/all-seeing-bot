from re import sub
from Starboard.utils import get_star_ammount


async def reaction_removed(reaction, user, bot, data):
	msg = reaction.message
	guild = msg.guild
	if str(reaction) == '⭐':
		leaderboard = data.get_leaders(guild)
		msg = reaction.message
		reactions = msg.reactions
		stars = await get_star_ammount(reactions, msg)
		star_dict = data.get_star(guild)
		msg_dict = data.get_msg(guild)
		stars_needed = data.get_data(guild)['min']

		star_channel = guild.get_channel(
			int(data.get_data(guild)['channel'])
		)
		if str(msg.id) in star_dict or str(msg.id) in msg_dict:
			if str(msg.id) in star_dict:

				other_post_id = star_dict[str(msg.id)]
				other_msg = await star_channel.fetch_message(int(other_post_id))
				other_reactions = other_msg.reactions
				embed = other_msg.embeds[0]
				user = msg.author
				bots_msg = False

			else:
				other_post_info = msg_dict[str(msg.id)]
				other_post_id = other_post_info[0]
				other_post_channel = other_post_info[1]
				other_post_channel = guild.get_channel(int(other_post_channel))
				other_msg = await other_post_channel.fetch_message(int(other_post_id))
				other_reactions = other_msg.reactions
				embed = msg.embeds[0]
				bots_msg = True
				user = other_msg.author

			stars = await get_star_ammount(
				reactions,
				msg,
				other=other_reactions,
				author=other_msg.author
			)

			embed.set_footer(text=f'⭐: {stars}')

			if user != bot.user:
				if bots_msg:
					await msg.edit(embed=embed)

				else:
					await other_msg.edit(embed=embed)
			lb_user_stars = leaderboard[str(user.id)]
			lb_user_stars -= 1
			leaderboard[str(user.id)] = lb_user_stars
			if stars < stars_needed:

				if bots_msg:
					await msg.delete()
					del msg_dict[str(msg.id)]
					del star_dict[str(other_msg.id)]

				else:
					await other_msg.delete()
					del msg_dict[str(other_msg.id)]
					del star_dict[str(msg.id)]

				lb_user_stars -= stars
				if lb_user_stars <= 0:
					del leaderboard[str(user.id)]
				else:
					leaderboard[str(user.id)] = lb_user_stars
				await data.set_star(guild, star_dict)
				await data.set_msg(guild, msg_dict)
			if lb_user_stars <= 0:
				del leaderboard[str(user.id)]
			await data.set_leaders(guild, leaderboard)
