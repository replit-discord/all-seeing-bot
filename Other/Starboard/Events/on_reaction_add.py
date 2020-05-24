from re import findall
from Other.Starboard.utils import get_embed, get_star_ammount, image_types


async def reaction_added(reaction, user, bot, data):

    msg = reaction.message
    author = msg.author
    guild = msg.guild
    if str(reaction) == '⭐':
        leaderboard = data.get_leaders(guild)
        msg = reaction.message
        channel = msg.channel
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

            stars = await get_star_ammount(
                reactions,
                msg,
                other=other_reactions,
                author=other_msg.author
            )

            embed.set_footer(text=f'⭐: {stars}')

            if bots_msg:
                await msg.edit(embed=embed)
                user = other_msg.author

            else:
                user = author

                await other_msg.edit(embed=embed)
            await data.set_leaders(guild, leaderboard)
            leaderboard[str(user.id)] += 1
        elif author != bot.user:

            stars = await get_star_ammount(reactions, msg)
            if stars >= stars_needed:

                user = author
                image_found = False

                for a in msg.attachments:
                    for n in image_types:

                        if n in a.url:
                            image_found = True
                            image_url = a.url

                    if image_found:
                        break
                if not image_found:
                    links = findall(
                        r'''(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<'
						'>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|['
						'^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?''',
                        msg.content
                    )

                    for a in links:
                        for n in image_types:

                            if n in a:
                                image_found = True
                                image_url = a

                        if image_found:
                            break

                if image_found:
                    embed = get_embed(stars, msg, image_url)
                else:
                    embed = get_embed(stars, msg)

                if str(msg.id) not in data.get_star(guild):
                    if user.id in leaderboard:
                        leaderboard[str(user.id)] += stars

                    else:
                        leaderboard[str(user.id)] = stars

                    other_msg = await star_channel.send(embed=embed)
                    await other_msg.add_reaction('⭐')
                    msg_dict[str(other_msg.id)] = [
                        str(msg.id), str(channel.id)]
                    star_dict[str(msg.id)] = str(other_msg.id)
                    await data.set_star(guild, star_dict)
                    await data.set_msg(guild, msg_dict)

                else:
                    leaderboard[str(user.id)] += 1

                await data.set_leaders(guild, leaderboard)
