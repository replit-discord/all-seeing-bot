import discord
from datetime import datetime

image_types = [  # Recognized image types
    'jpg',
    'jpeg',
    'gif',
    'png',  # the best one...
    'webp'
]


def channel_enabled(guild, channel_id, data, kind):
    if kind == 'c':
        fd = data.get_data(guild)
        channels_on = fd['channel_on']
        channels = fd['channels']
        channels.remove('None')
        if len(channels) != 0:
            channels = [int(c) for c in channels]

            if channel_id in channels:
                listed = True

            else:
                listed = False

            if channels_on:
                return listed

            else:
                return not listed

        else:
            if channels_on:
                return False

            else:
                return True

    elif kind == 'r':
        fd = data.get_data(guild)
        channels_on = fd['rchannel_on']
        channels = fd['rchannels']
        if 'None' in channels:
            channels.remove('None')
        channels = [int(c) for c in channels]
        if channel_id in channels:
            listed = True

        else:
            listed = False
        if channels_on:
            return listed

        else:
            return not listed


def get_embed(stars, msg, image=None):
    author = msg.author
    content = msg.content
    guild = msg.guild
    channel = msg.channel
    link = f'https://discordapp.com/channels/{guild.id}/{channel.id}/{msg.id}'
    embed = discord.Embed(
        title='**View Message**',
        color=0xffff00,
        url=link
    )
    embed.set_thumbnail(url=author.avatar_url)
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    embed.timestamp = datetime.now()
    if len(msg.embeds) == 0:
        fields = [
            ('**Content:**', content, True),
            ('**Channel:**', f'<#{channel.id}>', True),
            ('**Author:**', f'<@{author.id}>', True)
        ]
        if image is not None:
            embed.set_image(image)
            fields.append(
                ('**Image:**', '​', False)
            )
    else:
        print('done oofed')

        msg_embed = msg.embeds[0]
        desc = msg_embed.description
        fields = [
            ('**Content:**', content, True),
            ('**Channel:**', f'<#{channel.id}>', True),
            ('**Author:**', f'<@{author.id}>', True)
        ]
        title = msg_embed.title
        fields.append(
            ('​', '​', False)
        )
        fields.append(
            ('**Embed Title:**', title, True)
        )
        if desc != discord.Embed.Empty:
            fields.append(
                ('**Embed Description:**', desc, True)
            )

        if len(msg_embed.fields) > 0:
            fields.append(
                ('**Embed Fields**', '​', False)
            )
            for f in msg_embed.fields:
                fields.append(
                    (f.name, f.value, f.inline)
                )

        if content == '':
            fields.remove(
                ('**Content:**', content, True)
            )
        print(image)
        if image is not None:
            embed.set_image(url=image)
            fields.append(
                ('**Image:**', '​', False)
            )

    for field in fields:
        print(field)
        embed.add_field(
            name=field[0],
            value=field[1],
            inline=field[2]
        )
    embed.set_footer(text=f'⭐: {stars}')
    return embed


async def get_star_ammount(reactions, msg, **kwargs):
    # Gets the ammount of stars plus the ammount of stars already counted
    check_users = False

    for key, value in kwargs.items():

        if key == 'other':
            other_reactions = value
            check_users = True

        if key == 'author':
            other_author = value

    author = msg.author
    star_users = []
    for r in reactions:
        if str(r.emoji) == '⭐':
            # Converts the emoji to a string in the case that it is a custom emoji
            star_users = await r.users().flatten()

    if check_users:
        user_list = []
        for r in other_reactions:
            if str(r.emoji) == '⭐':
                user_list = await r.users().flatten()

        user_list += star_users
        user_list = list(dict.fromkeys(user_list))

        while author in user_list:
            user_list.remove(author)

        while other_author in user_list:
            user_list.remove(other_author)

        stars = len(user_list)

    else:

        if author in star_users:
            star_users.remove(author)

        stars = len(star_users)

    return stars
