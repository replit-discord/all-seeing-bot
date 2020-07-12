import discord
import asyncio
from datetime import datetime
from discord.ext import commands
from utils import get_muted_role, perm_cache
from tools.read_write import read, write
from utils import find_date, InvalidDate


def testFunc(ctx: commands.Context) -> bool:
    print('work bruh')
    print("guild id bruh", c.guild.id == 437048931827056642)
    return c.guild.id == 437048931827056642


class Moderation(commands.Cog, name='moderation'):
    '''Moderation Commands'''

    def __init__(self, bot):
        self.bot = bot
        self.color = 0xd91111

    async def log(
            self,
            ctx,
            desc,
            title='**Moderation**',
            color=0xff0000,
            **kwargs
    ):

        guild = ctx.guild
        log_embed = discord.Embed(
            title=title,
            description=desc,
            color=color
        )
        for key, value in kwargs.items():
            if key == 'fields':
                for field in value:
                    if len(field) == 2:
                        log_embed.add_field(
                            name=field[0],
                            value=field[1]
                        )
                    else:
                        log_embed.add_field(
                            name=field[0],
                            value=field[1],
                            inline=field[2]
                        )
            if key == 'showauth':
                if value:
                    author = ctx.author
                    disp_name = author.display_name
                    icon_url = author.avatar_url
                    log_embed.set_author(
                        name=disp_name,
                        icon_url=icon_url
                    )
                    log_embed.set_thumbnail(
                        url=icon_url
                    )
        now = datetime.now()
        log_embed.timestamp = now
        log_dict = await read('al')
        action_log_id = log_dict[guild.id]
        log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
        await log_channel.send(embed=log_embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, role, _):
        perm_cache.reset(role.guild.id)

    @commands.Cog.listener()
    async def on_member_update(self, user, _):
        perm_cache.reset_user(user)

    @commands.command(name='banword', aliases=['bw'])
    async def ban_word(self, ctx, word: str, paranoia: int):
        '''Bans a phrase from user messages.
        ```css
        Example Usage:
        ``````py
        ?banword badword 0  # Bans "badword from messages with level 0 paranoia."
        ``````py
        ?bw badword 2  # Bans "bad word" from messages with paranoia level 2.


        Levels of paranoia:
        ```k
        (assume "badword" is banned)
        0 | Exact word - badword (✓) bad word (✓) motherbadword (x) nobadwordplz (x)
        1 | Root word match - badword (✓) bad word (✓) motherbadword (✓) nobadwordplz (x)
        2 | Any match - badword (✓) bad word (✓) motherbadword (✓) nobadwordplz (✓)
        ```

        '''
        msg = ctx.message
        guild = ctx.guild
        author = ctx.author
        fd = await read('banWords', True, False)

        if guild.id in fd:
            guild_list = fd[guild.id]

        else:
            guild_list = []

        if word.lower() not in [w['word'] for w in guild_list]:
            print('appending')
            guild_list.append({'word': word.lower(), 'paranoia': paranoia})

        else:
            await ctx.send(
                f"`{word}` is already in the server's ban list!"
            )
            return

        fd[guild.id] = guild_list
        await write('banWords', fd, False)
        await self.log(
            ctx,
            f"<@{author.id}> added `{word}` to the server's ban list.",
            '**Banword**',
            showauth=True
        )
        await ctx.send(f"`{word}` has been added to the server's ban list.")

    @commands.command(name='unbanword', aliases=['unbw'])
    async def unban_word(self, ctx, word: str):
        '''Unbans a string or word from user messages.
        ```css
        example usage:
        ``````fix
        unbanword allseeingbot
        ``````fix
        unbw all seeing bot'''
        msg = ctx.message
        guild = ctx.guild
        author = ctx.author
        fd = await read('banWords', True, False)

        if guild.id in fd:
            guild_list = fd[guild.id]

        else:
            guild_list = []

        word = [w for w in guild_list if w['word'] == word]

        if words == []:
            await ctx.send(
                f"`{word}` is not in the server's ban list!"
            )

        word = word[0]

        guild_list.remove(word)

        fd[guild.id] = guild_list
        await write('banWords', fd, False)
        await self.log(
            ctx,
            f"<@{author.id}> removed `{word}` from the server's ban list.",
            '**Banword**',
            showauth=True
        )
        await ctx.send(f"`{word}` has been removed from the server's ban list.")

    @commands.command(name='banreaction', aliases=['br'])
    async def ban_reaction(self, ctx, *_):
        '''Bans a reaction.
        ```css
        Example Usage:
        ``````css
        ?banreaction ✅ //Bans the reaction ✅
        ```'''
        msg = ctx.message
        guild = ctx.guild
        author = ctx.author
        phrase = msg.content.split(None, 1)[1]
        lower_phrase = phrase.lower()
        fd = await read('banEmojis', True, False)

        if guild.id in fd:
            guild_list = fd[guild.id]

        else:
            guild_list = []

        if lower_phrase not in guild_list:
            guild_list.append(lower_phrase)
            failed = False

        else:
            await ctx.send(
                f"`{phrase}` is already in the server's ban list!"
            )
            failed = True

        if not failed:
            fd[guild.id] = guild_list
            await write('banEmojis', fd, False)
            await self.log(
                ctx,
                f"<@{author.id}> added `{phrase}` to the server's ban list.",
                '**Ban reaction**',
                showauth=True
            )
            await ctx.send(f"`{phrase}` has been added to the server's ban list.")

    @commands.command(name='unbanreaction', aliases=['unbr'])
    async def unban_reaction(self, ctx, *_):
        '''Unbans a reaction.
        ```css
        Example Usage:
        ``````css
        ?unbanreaction ✅ // Allows users to react to messages with the ✅ emoji again
        ```'''
        msg = ctx.message
        guild = ctx.guild
        author = ctx.author
        phrase = msg.content.split(None, 1)[1]
        lower_phrase = phrase.lower()
        fd = await read('banEmojis', True, False)

        if guild.id in fd:
            guild_list = fd[guild.id]

        else:
            guild_list = []

        if lower_phrase in guild_list:
            guild_list.remove(lower_phrase)
            failed = False

        else:
            await ctx.send(
                f"`{phrase}` is not in the server's ban list!"
            )
            failed = True

        if not failed:
            fd[guild.id] = guild_list
            await write('banEmojis', fd, False)
            await self.log(
                ctx,
                f"<@{author.id}> removed `{phrase}` from the server's ban list.",
                '**Banreaction**',
                showauth=True
            )
            await ctx.send(f"`{phrase}` has been removed from the server's ban list.")

    @commands.command(name='banlist')
    async def list_banned_content(self, ctx):
        '''Get a list of banned words and reactions in the server.
        ```css
        Example Usage:
        ``````css
        ?banlist // Get a list of all banned words and reactions in the server.
        ```'''
        guild = ctx.guild
        fd = await read('banWords', True, False)
        if guild.id not in fd:
            fd[guild.id] = []
            await write('banWords', fd, False)
        ban_words = fd[guild.id]
        fd = await read('banEmojis', True, False)
        if guild.id not in fd:
            fd[guild.id] = []
            await write('banEmojis', fd, False)
        ban_emojis = fd[guild.id]
        embed = discord.Embed(
            title='**Banned Content:**',
            color=0xeb5e34
        )
        if ban_words is not []:
            ban_word_content = '```css\n'
            for a in range(len(ban_words)):
                word = ban_words[a]
                paranoia = word['paranoia']

                ban_word_content += f'{a+1}: (Paranoia: {paranoia}) {word["word"]}\n'
            ban_word_content += '```'
        else:
            ban_word_content = 'None'
        if ban_emojis is not []:
            ban_emoji_content = '```css\n'
            for a in range(len(ban_emojis)):
                ban_emoji_content += f'{a+1}: {ban_emojis[a]}\n'

            ban_emoji_content += '```'
        else:
            ban_emoji_content = 'None'
        embed.add_field(
            name='**Banned Words:**',
            value=ban_word_content,
            inline=True
        )
        embed.add_field(
            name='**Banned Reactions:**',
            value=ban_emoji_content,
            inline=True
        )
        # print(ban_emoji_content)
        await ctx.send(embed=embed)

    @commands.command(name='kick', aliases=['k'])
    async def kick(self, ctx, user: discord.Member, *_):
        '''Kick a user.
        ```css
        Example Usage:```
        ```css
        ?kick <user> bc i can // Kicks <user> for bc i can```'''
        msg = ctx.message
        author = ctx.author
        try:
            reason = msg.content.split(None, 1)[1]
            found_reason = True
        except IndexError:
            found_reason = False
        if found_reason:
            await self.log(
                ctx,
                f'<@{author.id} kicked <@{user.id}>',
                fields=[
                    ('**Reason:**', reason)
                ]
            )
            await user.kick(reason=reason)
        else:
            await self.log(
                ctx,
                f'<@{author.id}> kicked <@{user.id}>'
            )
            await user.kick()

    @commands.command(name='ban')
    async def ban(self, ctx, user: discord.Member, time=None, *argv):
        '''Ban a user.
        ```css
        Example Usage:
        ```
        ```css
        ?ban <user> bc i can// Bans <user> from the guild for the reason bc i can
        ``````css
        ?ban <user> 5d bc i can // Bans <user> for 5 days with the reason bc i can'''
        fields = []
        guild = ctx.guild
        if time is not None:
            try:
                duration = find_date(time)
                end_date = duration + datetime.now()

                end_date.strftime('%Y-%m-%w-%W %H:%M:%S')
                ban_list = await read('banList')
                if guild.id in ban_list:
                    guild_list = ban_list[guild.id]
                else:
                    guild_list = {}
                guild_list[user.id] = end_date
                ban_list[guild.id] = guild_list
                await write('banList', ban_list)
                fields.append(
                    ('**Duration:**', f'`{time}`', True)
                )
            except InvalidDate:
                argv = list(argv)
                argv.insert(0, time)

        author = ctx.author
        if len(argv) > 0:
            reason = ' '.join(argv)
            fields.append(
                ('**Reason:**', reason, True)
            )

        await self.log(
            ctx,
            f'<@{author.id}> banned <@{user.id}>',
            fields=fields,
            showauth=True
        )
        embed = discord.Embed(
            title='**Ban**',
            description=f'<@{user.id}> has been banned.',
            color=0xff0000
        )
        await user.ban()
        await ctx.send(embed=embed)

    @commands.command(name='unban', aliases=['pardon'])
    async def unban(self, ctx, user: discord.User, *argv):
        '''Unban a user from the guild.
        ```css
        Example Usage:
        ``````css
        ?unban <user id> i didnt mean to ban them // Unbans the user with the id <user id> from the guild
        ```'''
        fields = []
        guild = ctx.guild

        ban_list = await read('banList')
        if guild.id in ban_list:
            if user.id in ban_list:
                del ban_list[guild.id][user.id]
                await write('banList', ban_list)

        author = ctx.author
        try:
            reason = ' '.join(argv)
            fields.append(
                ('**Reason:**', reason, True)
            )
        except IndexError:
            pass

        await self.log(
            ctx,
            f'<@{author.id}> unbanned <@{user.id}>',
            fields=fields,
            showauth=True
        )

    @commands.command(name='mute', aliases=['silence'])
    async def mute(self, ctx, user: discord.Member, time=None, *argv):
        '''Mute a user so that they cannot send messages anymore.
        ```css
        Example Usage:
        ``````css
        ?mute <user> 5d bc i can // Mutes <user> for 5 days with the reason because i can.
        ``````css
        ?mute <user> bc i can // Mutes <user> permanately for reason bc i can
        ```'''

        fields = []
        guild = ctx.guild
        if time is not None:
            try:
                duration = find_date(time)
                end_date = duration + datetime.now()

                end_date = end_date.strftime('%Y-%m-%w-%W %H:%M:%S')
                mute_list = await read('muteList')
                if str(guild.id) in mute_list:
                    guild_list = mute_list[str(guild.id)]
                else:
                    guild_list = {}
                guild_list[user.id] = end_date

                mute_list[str(guild.id)] = guild_list
                await write('muteList', mute_list)
                fields.append(
                    ('**Duration:**', f'`{time}`', True)
                )
            except InvalidDate:
                argv = list(argv)
                argv.insert(0, time)

        author = ctx.author
        if len(argv) > 0:
            reason = ' '.join(argv)
            fields.append(
                ('**Reason:**', reason, True)
            )

        await self.log(
            ctx,
            f'<@{author.id}> muted <@{user.id}>',
            fields=fields,
            showauth=True
        )
        muted_role = await get_muted_role(guild)
        await user.add_roles(muted_role)
        embed = discord.Embed(
            title='**Mute**',
            description=f'<@{user.id}> has been muted.',
            color=0xff0000
        )
        await ctx.send(embed=embed)

    @commands.command(name='unmute')
    async def unmute(self, ctx, user: discord.Member, *argv):
        '''Unmute a user.
        ```css
        Example usage:
        ``````css
        ?unmute <user> oops wrong person // Unbans <user> for the reason oops wrong person.
        ```'''
        fields = []
        guild = ctx.guild

        mute_list = await read('muteList')
        if guild.id in mute_list:
            if user.id in mute_list:
                del mute_list[guild.id][user.id]
                await write('muteList', mute_list)

        author = ctx.author
        try:
            reason = ' '.join(argv)
            fields.append(
                ('**Reason:**', reason, True)
            )
        except IndexError:
            pass

        await self.log(
            ctx,
            f'<@{author.id}> unmuted <@{user.id}>',
            fields=fields,
            showauth=True
        )
        muted_role = await get_muted_role(guild)
        await user.remove_roles(muted_role)

    @commands.command(name='warn', aliases=['hint', 'suggest'])
    async def warn(self, ctx, user: discord.Member, *argv):
        '''Warn a user.
        ```css
        Example Usage:
        ``````css
        ?warn <user> dont say that word // Warns <user> dont say that word.```'''
        guild = ctx.guild
        author = ctx.author
        warn_dict = await read('warn_list')
        reason = ' '.join(argv)
        if str(guild.id) in warn_dict:
            guild_warn_dict = warn_dict[str(guild.id)]

        else:
            guild_warn_dict = {}

        date = datetime.now()
        date_str = date.strftime('%Y-%m-%w-%W %H:%M:%S')
        if str(user.id) in guild_warn_dict:
            user_warns = guild_warn_dict[str(user.id)]
        else:
            user_warns = []

        warn_info = {
            'type': 'warn',
            'moderator': author.id,
            'reason': reason,
            'date': date_str
        }

        user_warns.append(warn_info)

        guild_warn_dict[str(user.id)] = user_warns

        warn_dict[str(guild.id)] = guild_warn_dict

        await write('warn_list', warn_dict)
        warn_embed = discord.Embed(
            title='**You have been warned.**',
            description=f'You have been warned on `{guild.name}`.',
            color=0xff0000
        )
        warn_embed.add_field(
            name='**Reason:**',
            value=reason
        )
        await user.send(embed=warn_embed)

        await self.log(
            ctx,
            f'<@{author.id}> warned <@{user.id}>.',
            title='**Warn**',
            fields=[('**Warn Content:**', reason)],
            showauth=True
        )
        embed = discord.Embed(
            title='**Warn**',
            description=f'Warned <@{user.id}>.',
            color=0xff0000
        )
        await ctx.send(embed=embed)

    @commands.command(name='strike')
    async def strike(self, ctx, user: discord.Member, *argv):
        '''Strike a user.
        ```css
        Example Usage:
        ``````css
        ?strike <user> dont say that word // Strikes <user> for dont say that word.```'''
        guild = ctx.guild
        author = ctx.author
        warn_dict = await read('warn_list')
        reason = ' '.join(argv)
        if str(guild.id) in warn_dict:
            guild_warn_dict = warn_dict[str(guild.id)]

        else:
            guild_warn_dict = {}

        date = datetime.now()
        date_str = date.strftime('%Y-%m-%w-%W %H:%M:%S')
        if str(user.id) in guild_warn_dict:
            user_warns = guild_warn_dict[str(user.id)]
        else:
            user_warns = []

        warn_info = {
            'type': 'strike',
            'moderator': author.id,
            'reason': reason,
            'date': date_str
        }

        user_warns.append(warn_info)

        guild_warn_dict[str(user.id)] = user_warns

        warn_dict[str(guild.id)] = guild_warn_dict

        await write('warn_list', warn_dict)
        warn_embed = discord.Embed(
            title='**You have been striked.**',
            description=f'You have been striked in `{guild.name}`.',
            color=0xff0000
        )
        warn_embed.add_field(
            name='**Reason:**',
            value=reason
        )
        await user.send(embed=warn_embed)

        await self.log(
            ctx,
            f'<@{author.id}> warned <@{user.id}>.',
            title='**Strike**',
            fields=[('**Strike Reason:**', reason)],
            showauth=True
        )
        embed = discord.Embed(
            title='**Strike**',
            description=f'Striked <@{user.id}>.',
            color=0xff0000
        )
        await ctx.send(embed=embed)

    @commands.command(name='selfhistory')
    async def self_history(self, ctx):
        '''List a user's warns.
        ```css
        Example Usage:
        ``````css
        ?history <user> // Get a list of <user>'s warns'''
        user = ctx.author
        warns = await read('warn_list')

        guild = ctx.guild
        if str(guild.id) not in warns:
            await user.send("User has not been warned.")
            return

        guild_warns = warns[str(guild.id)]

        if str(user.id) not in guild_warns:
            await user.send("User has not been warned.")
            return

        user_warns = guild_warns[str(user.id)]

        if len(user_warns) == 0:
            await user.send("User has not been warned.")
            return

        fields = []
        warn_count = 0
        strike_count = 0
        icin = 0

        for w in user_warns:

            if w['type'] == 'strike':
                strike_count += 1
            else:
                warn_count += 1

            value = ''

            value += f'Type: **{w["type"]}**\n'
            value += f'Reason: ***{w["reason"]}***\n'
            value += f'Timestamp: **{w["date"]}**'
            # print(value)
            fields.append((f'ICIN **{icin}**:', value))
            icin += 1

        max_warn_counts = await read('wl')
        if guild.id in max_warn_counts:
            max_warns = max_warn_counts[guild.id]
        else:
            max_warns = 3

        max_strike_counts = await read('sl')
        if guild.id in max_strike_counts:
            max_strikes = max_strike_counts[guild.id]
        else:
            max_strikes = 5

        strikes_from_warns = int(
            (warn_count - (warn_count % max_warns)) / max_warns)
        remaining_warns = warn_count % max_warns
        created_at = user.created_at
        created_at_str = created_at.strftime('%Y-%m-%w-%W %H:%M:%S')
        desc = f'''
		Total Warnings: **{remaining_warns}/{max_warns}**
		Total Strikes: **{strikes_from_warns + strike_count}/{max_strikes}**
		Strikes from warnings: **{strikes_from_warns}**
		Account Creation Date: **{created_at_str}**
		'''

        embed = discord.Embed(
            title=f"{user.display_name}'s History",
            description=desc,
            color=0x8002d4
        )

        embed.set_thumbnail(url=user.avatar_url)

        for f in fields:
            embed.add_field(
                name=f[0],
                value=f[1],
                inline=False
            )

        await user.send(embed=embed)

    @commands.command(name='history', aliases=['warnlist', 'listwarns'])
    async def get_warns(self, ctx, user: discord.Member):
        '''List a user's warns.
        ```css
        Example Usage:
        ``````css
        ?history <user> // Get a list of <user>'s warns'''
        # print("bruhe")
        warns = await read('warn_list')

        guild = ctx.guild
        if str(guild.id) not in warns:
            await ctx.send("User has not been warned.")
            return

        guild_warns = warns[str(guild.id)]

        if str(user.id) not in guild_warns:
            await ctx.send("User has not been warned.")
            return

        user_warns = guild_warns[str(user.id)]

        if len(user_warns) == 0:
            await ctx.send("User has not been warned.")
            return

        fields = []
        warn_count = 0
        strike_count = 0
        icin = 0

        for w in user_warns:

            if w['type'] == 'strike':
                strike_count += 1
            else:
                warn_count += 1

            value = ''

            value += f'Type: **{w["type"]}**\n'
            value += f'Reason: ***{w["reason"]}***\n'
            value += f'Moderator: **<@{w["moderator"]}>**\n'
            value += f'Timestamp: **{w["date"]}**'
            # print(value)
            fields.append((f'ICIN **{icin}**:', value))
            icin += 1

        max_warn_counts = await read('wl')
        if guild.id in max_warn_counts:
            max_warns = max_warn_counts[guild.id]
        else:
            max_warns = 3

        max_strike_counts = await read('sl')
        if guild.id in max_strike_counts:
            max_strikes = max_strike_counts[guild.id]
        else:
            max_strikes = 5

        strikes_from_warns = int(
            (warn_count - (warn_count % max_warns)) / max_warns)
        remaining_warns = warn_count % max_warns
        created_at = user.created_at
        created_at_str = created_at.strftime('%Y-%m-%w-%W %H:%M:%S')
        desc = f'''
		Total Warnings: **{remaining_warns}/{max_warns}**
		Total Strikes: **{strikes_from_warns + strike_count}/{max_strikes}**
		Strikes from warnings: **{strikes_from_warns}**
		Account Creation Date: **{created_at_str}**
		'''

        embed = discord.Embed(
            title=f"{user.display_name}'s History",
            description=desc,
            color=0x8002d4
        )

        embed.set_thumbnail(url=user.avatar_url)

        for f in fields:
            embed.add_field(
                name=f[0],
                value=f[1],
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='repeal')
    async def pardon_warn(self, ctx, user: discord.Member, icin: int, *reason):
        '''Remove a users warning or strike.
        ```css
        Example Usage:
        ``````css
        ?removewarn <user> <icin> // remove's <user>'s <icin> warn.
'''
        warn_dict = await read('warn_list')
        guild = ctx.guild

        if str(guild.id) not in warn_dict:
            await ctx.sent("User has not been warned.")
            return

        guild_warns = warn_dict[str(guild.id)]

        if str(user.id) not in guild_warns:
            await ctx.send("User has not been warned.")
            return

        user_warns = guild_warns[str(user.id)]
        if not len(user_warns) > icin:
            await ctx.send(f"{user.display_name} only has {len(user_warns)} icins.")
            return

        del user_warns[icin]

        guild_warns[str(user.id)] = user_warns
        warn_dict[str(guild.id)] = guild_warns
        await write('warn_list', warn_dict)
        await ctx.send("Warning / strike removed.")

    @commands.command(name="helper")
    @commands.check(testFunc)
    async def toggle_helper_role(ctx: commands.Context, name: str):

        role = await commands.RoleConverter.convert(ctx, f'help-{name}')

        if not role:
            await ctx.send("nope nope doesnt exist rip")
            return

        if role in ctx.author.roles:
            await ctx.author.remove_role(role)
        else:
            await ctx.author.add_role(role)

        await ctx.send('done')

    @commands.command(name='purge')
    async def purge(self, ctx, ammount: int, user: discord.Member = None):
        '''
        Bulk delete messages in a channel.
        ```css
        Example Usage:
        ``````css
        ?purge 20 // Purges the last 20 messages in the channel
        ``````css
        ?purge 20 @baduser#1234 // Purge the last 20 messages by @baduser#1234 in the channel.
        ```
        '''
        channel = ctx.channel
        if ammount > 200:
            await ctx.send("You can't delete more than 200 messages at at time.")

        def check_user(message):
            return message.author == user

        msg = await ctx.send('Purging messages.')
        if user is not None:
            class count_num:
                def __init__(self):
                    self.value = 0

                def __ge__(self, other: int):
                    return self.value >= other

                def add(self):
                    self.value += 1
                    return self.value
            msg_number = count_num()

            def msg_check(x):

                if msg_number >= ammount:
                    return False
                if x.id != msg.id and x.author == user:
                    msg_number.add()
                    return True
                return False

            msgs = await channel.purge(
                limit=100,
                check=msg_check,
                bulk=True
            )
            await self.log(
                ctx,
                f"{len(msgs)} of <@{user.id}>'s messages were "
                f"deleted by <@{ctx.author.id}>",
                '**Message Purge**',
                showauth=True
            )
            # print(msg in msgs, len(msgs))
        else:

            msgs = await channel.purge(
                limit=ammount + 2,
                check=lambda x: x.id != msg.id,
                bulk=True
            )
            await self.log(
                ctx,
                f'{len(msgs)} messages were deleted by <@{ctx.author.id}>',
                '**Message Purge**',
                showauth=True
            )
            # print(msg in msgs)

        await msg.edit(content='Deleted messages.')
        await asyncio.sleep(2)
        await msg.delete()


def setup(bot):
    bot.add_cog(Moderation(bot))
