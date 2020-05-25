import discord
from datetime import datetime
from Other.Starboard.data import data
from discord.ext import commands
from Other.Starboard.utils import channel_enabled
from Other.Starboard.Events.on_reaction_add import reaction_added
from Other.Starboard.Events.on_reaction_remove import reaction_removed

with open('.config/pycodestyle', 'w') as f:
    f.write('[pycodestyle]\nignore = W191, E701')


def check_channel(ctx):
    channel = ctx.channel
    author = ctx.author
    guild = ctx.guild
    if author.guild_permissions.administrator:
        return True
    else:
        return channel_enabled(guild, channel.id, data, 'c')


class Starboard(commands.Cog, name='starboard'):
    '''Starboard commands'''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await data.init()

        print('Bot Ready')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await data.reset(guild)

    @commands.has_permissions(administrator=True)
    @commands.command(name='reset')
    async def reset(self, ctx):
        '''Resets the guild data for starboard.
This command resets the
•star count
•prefix
•minimum number of stars required
•white/blacklisted channels

Example Usage:
``````css
?reset
'''
        guild = ctx.guild
        await data.reset(guild)
        await ctx.send('Guild data for starboard has been reset.')

    @commands.has_permissions(administrator=True)
    @commands.command(
        name='togglelist', aliases=['tl', 'whitelist', 'blacklist'])
    async def togglelist(self, ctx):
        '''Toggles the (command) black/whitelisting of the channel list.

        If the channel list is a whitelist, the user may use starboard commands in the channels in the list.

        If the channel list is a blacklist instead, users may use the starboard commands in every channel in the guild but those in the list.

        Example Usage:
        ``````css
        ?togglelist
        ``````css
        ?tl
        '''
        fd = data.get_data(ctx.guild)
        channel_on = fd['channel_on']

        channel_on = not channel_on
        fd['channel_on'] = channel_on
        if channel_on:
            title = '**Command Whitelist**'
            desc = 'Command channel whitelist has been enabled.'
            color = 0x00940c
            footer = 'All channels in the channel list are now whitelisted '
            'from the Command'

        else:
            title = '**Command Blacklist**'
            desc = 'Command channel blacklist has been enabled.'
            color = 0x940000
            footer = 'All channels in the channel list are now blacklisted '
            'from the Command'

        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)
        await data.set_data(ctx.guild, fd)

    @commands.has_permissions(administrator=True)
    @commands.command(
        name='rtogglelist', aliases=['rtl', 'rwhitelist', 'rblacklist'])
    async def rtogglelist(self, ctx):
        '''Toggles the (starboard) black/whitelisting of the channel list.

        If the channel list is a whitelist, the stars in channels in the list will be considered for starboard.

        If the channel list is a blacklist instead, stars in every channel but those in the list will be considered.

        Example Usage:
        `````css
        ?rtogglelist
        ``````css
        ?rtl
        '''
        fd = data.get_data(ctx.guild)
        channel_on = fd['rchannel_on']

        channel_on = not channel_on

        fd['rchannel_on'] = channel_on
        if channel_on:
            title = '**Starboard Whitelist**'
            desc = 'Starboard channel whitelist has been enabled.'
            color = 0x00940c
            footer = 'All channels in the channel list are now whitelisted '
            'from the starboard'

        else:
            title = '**Starboard Blacklist**'
            desc = 'Starboard channel blacklist has been enabled.'
            color = 0x940000
            footer = 'All channels in the channel list are now blacklisted '
            'from the starboard'

        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)
        await data.set_data(ctx.guild, fd)

    @commands.has_permissions(administrator=True)
    @commands.command(name='togglechannel', aliases=['tc'])
    async def togglechannel(self, ctx, channel: discord.TextChannel = None):
        '''Adds or removes channel to the command black/whitelist.

                        Example Usage:
                        ``````css
                        ?togglechannel
                        ``````css
                        ?tc
                        '''

        fd = data.get_data(ctx.guild)
        channels = fd['channels']

        if channel.id in channels:
            channels.remove(str(channel.id))
            change = 'removed'

        else:
            channels.append(str(channel.id))
            change = 'added'

        fd['channels'] = channels

        if fd['channel_on']:
            desc = f'<#{channel.id}> has been {change} to the command whitelist'
        else:
            desc = f'<#{channel.id}> has been {change} to the command blacklist'

        embed = discord.Embed(
            title='**Channel Toggle**', description=desc, color=0x00ff88)
        prefix = data.get_data(ctx.guild)['prefix']
        embed.set_footer(text=f'Use {prefix}tl to toggle black/whitelist')
        await ctx.send(embed=embed)
        await data.set_data(ctx.guild, fd)

    @commands.has_permissions(administrator=True)
    @commands.command(name='rtogglechannel', aliases=['rtc'])
    async def rtogglechannel(self, ctx, channel: discord.TextChannel = None):
        '''Add channel to the starboard black/whitelist.

                        Example Usage:
                        ``````css
                        ?rtogglechannel
                        ``````css
                        ?rtc'''

        fd = data.get_data(ctx.guild)
        channels = fd['rchannels']

        if channel.id in channels:
            channels.remove(channel.id)
            change = 'removed'

        else:
            channels.append(channel.id)
            change = 'added'

        fd['rchannels'] = channels

        if fd['rchannel_on']:
            desc = f'<#{channel.id}> has been {change} to the star whitelist'
        else:
            desc = f'<#{channel.id}> has been {change} to the star blacklist'

        embed = discord.Embed(
            title='**Channel Toggle**', description=desc, color=0x00ff88)
        prefix = data.get_data(ctx.guild)['prefix']
        embed.set_footer(text=f'Use {prefix}rtl to toggle black/whitelist')
        await ctx.send(embed=embed)
        await data.set_data(ctx.guild, fd)

    @commands.has_permissions(administrator=True)
    @commands.command(name='prefix')
    async def set_prefix(self, ctx, prefix: str):
        '''Sets the bot prefix.

                        Example Usage:
                        ``````css
                        ?prefix $'''
        bot_data = data.get_data(ctx.guild)
        if bot_data['prefix'] == prefix:
            desc = (f'The prefix is already `{prefix}`!')

        else:
            bot_data['prefix'] = prefix
            await data.set_data(ctx.guild, bot_data)
            self.bot.command_prefix = prefix
            desc = (f'Prefix has been changed to `{prefix}`.')

        embed = discord.Embed(
            title='**Prefix**', description=desc, color=0x00ffea)
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.command(
        name='setchannel', aliases=['sc', 'starchannel', 'starchan'])
    async def setchannel(self, ctx, channel: discord.TextChannel = None):
        '''Sets the starboard channel.

                        A channel can be mentioned in the command. In case any channel is not mentioned, the channel in which the message is sent is set as the starboard channel.

                        Example Usage:
                        ``````css
                        ?setchannel starboard //sets the starboard channel to a channel called starboard
                        ``````css
                        ?sc
                        ``````css
                        ?starchannel
                        ``````css
                        ?starchan
                        '''
        msg = ctx.message

        if channel is None:
            channel = msg.channel

        failed = False
        if not failed:
            fd = data.get_data(ctx.guild)
            fd['channel'] = str(channel.id)

            desc = f'Starboard channel set to <#{channel.id}>.'
            embed = discord.Embed(
                title='**Starboard Channel**',
                description=desc,
                color=0xff9500)
            await data.set_data(ctx.guild, fd)
            await ctx.send(embed=embed)

    @commands.command(name='fix')
    async def fix(self, ctx, msg_link: str):
        '''Fixes a message that should/shouldn't be in starboard.

                        use this command with a link to the message in question.

                        Example Usage:
                        ``````css
                        ?fix <message link>'''
        info = msg_link[32:].split('/')
        guild = self.bot.get_guild(int(info[0]))
        channel = guild.get_channel(int(info[1]))
        msg = await channel.fetch_message(int(info[2]))
        user = msg.author

        for r in msg.reactions:
            if str(r.emoji) == '⭐':
                reaction = r
        enabled = channel_enabled(guild, info[1], data, 'r')
        if enabled:
            await reaction_added(reaction, user, self.bot, data)

            await reaction_removed(reaction, user, self.bot, data)

            desc = 'Message has been fixed.'
            embed = discord.Embed(
                title="**Fix**", description=desc, color=0x000000)
            await ctx.send(embed=embed)
        else:
            await ctx.send('That channel is not enabled for the starboard!')

    @commands.command(name='leaderboard', aliases=['l', 'lb', 'leaders'])
    async def leaderboard(self, ctx, page: int = 1):
        '''Shows the leaderboard.

                        Example Usage:
                        ```````css
                        ?leaderboard (or) ?l (or) ?lb (or) ?leaders'''
        leader_list = data.get_leaders(ctx.guild)

        if 'None' in leader_list and len(leader_list):
            del leader_list['None']

        failed = False

        if len(leader_list) == 0:
            await ctx.send(
                'Nobody is on the leaderboard.'
                'You could be the first one!'
            )
            failed = True

        if (page - 1) * 10 > len(leader_list):
            await ctx.send('Invalid page number')
            failed = True

        if page <= 0:
            failed = True
            await ctx.send('Invalid page number.')

        if not failed:
            page -= 1
            leaders = data.get_leaders(ctx.guild)
            tup_list = [(k, v) for k, v in leaders.items()]

            sorted_board = sorted(
                tup_list, key=lambda tup: int(tup[1]), reverse=True)

            desc = '```css'
            pages = [
                sorted_board[n:n + 10] for n in range(0, len(sorted_board), 10)
            ]
            number = page * 10
            for a in pages[page]:
                user = ctx.guild.get_member(int(a[0]))
                stars = a[1]
                desc += f'\n{number+1}) {user.display_name}: {stars}'
                number += 1

            desc += '```'
            embed = discord.Embed(
                title='**Leaderboard**', description=desc, color=0xffffff)
            embed.set_thumbnail(
                url='http://bestanimations.com/Games/Awards/animated'
                '-first-place-medal-award2.gif'  # Cite: http://bestanimations.com
            )
            embed.set_footer(
                text=f'Use {ctx.prefix}l <page number> to select '
                f'a page number. Page {page + 1}/{len(pages)}'
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                'Invalid page number. Example command:'
                f'`{ctx.prefix}l 1`'
            )
        leader_list["None"] = 'None'
        await data.set_leaders(ctx.guild, leader_list)

    @commands.has_permissions(administrator=True)
    @commands.command(name='setmin', aliases=['min', 'setreq'])
    async def setmin(self, ctx, amount: int):
        '''Sets the required amount of stars for a message to be pinned.

                        Example Usage:
                        ``````css
                        ?setmin 5
                        ``````css
                        ?min 6
                        ``````css
                        ?setreq 12
                        '''
        fd = data.get_data(ctx.guild)
        fd['min'] = amount
        await data.set_data(ctx.guild, fd)
        desc = f'Minimum amount of stars set to `{amount}`.'
        embed = discord.Embed(
            title='**Star Minumum**', description=desc, color=0x73ff00)
        await ctx.send(embed=embed)

    # @commands.Cog.listener()
    async def on_command_error(self, ctx, Exception):
        '''if isinstance(Exception, commands.errors.MissingPermissions):
                desc = 'You do not have sufficent permissions to use this command.'

                embed = discord.Embed(
                        title="**Missing Permissions**",
                        description=desc,
                        color=0xff0000
                )
                embed.add_field(
                        name='Attempted Command:',
                        value=ctx.message.content
                )
                embed.set_footer(text=f'Command failed in #{ctx.channel.name}')
                await ctx.author.send(embed=embed)'''
        if isinstance(Exception, commands.errors.CheckFailure):
            pass
        elif isinstance(Exception, commands.errors.BadArgument):
            exception = str(Exception)
            msg = ctx.message

            author = ctx.author
            now = datetime.now()
            embed = discord.Embed(
                title='**Error**', description=exception, color=0xff0000)
            embed.timestamp = now
            embed.set_footer(text=msg.content)
            await author.send(embed=embed)

        else:
            raise Exception

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print(payload.emoji)
        if str(payload.emoji) == '⭐':
            guild_id = payload.guild_id
            guild = self.bot.get_guild(guild_id)
            channel_id = payload.channel_id
            enabled = channel_enabled(guild, channel_id, data, 'r')
            if enabled:
                msg_id = payload.message_id
                channel = guild.get_channel(channel_id)
                msg = await channel.fetch_message(msg_id)
                user = msg.author

                for r in msg.reactions:
                    if str(r.emoji) == '⭐':
                        reaction = r
                await reaction_added(reaction, user, self.bot, data)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        if str(payload.emoji) == '⭐':
            guild_id = payload.guild_id
            channel_id = payload.channel_id
            guild = self.bot.get_guild(guild_id)
            enabled = channel_enabled(guild, channel_id, data, 'r')
            if enabled:
                msg_id = payload.message_id

                channel = guild.get_channel(channel_id)
                msg = await channel.fetch_message(msg_id)
                user = msg.author

                for r in msg.reactions:
                    if str(r.emoji) == '⭐':
                        reaction = r
                try:
                    await reaction_removed(reaction, user, self.bot, data)
                except UnboundLocalError:
                    pass


def setup(bot):
    bot.add_cog(Starboard(bot))
