import os
import discord
from datetime import datetime
from tools.read_write import read, write
from utils import index_args, get_checks
from discord.ext import commands
from Moderation.spamchart import handle_infractions, handle_message, handle_banned_emoji, init
from Moderation.Message_Checks import checks


async def log(
        message: discord.Message,
        desc: str,
        title: str = '**Moderation**',
        color=0xff0000,
        **kwargs
):

    guild = message.guild
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
                author = message.author
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
    if guild.id in log_dict:
        action_log_id = log_dict[guild.id]
        log_channel = message.guild.get_channel(action_log_id)
        await log_channel.send(embed=log_embed)


class Checks(commands.Cog, name='moderation checks'):
    '''Customize checks everywhere or per channel!'''

    def __init__(self, bot):
        self.bot = bot
        self.user = bot.user
        self.color = 0xd64c1e
        init(self)

    async def log(
        self,
        message: discord.Message,
        desc: str,
        title: str = '**Moderation**',
        color=0xff0000,
        **kwargs
    ):
        print("yo")
        await log(message, desc, title, color, **kwargs)

    async def check_enabled(self, guild, name, channel=None, author=None):

        checks = await get_checks(
            guild.id,
            channel.id,
            author.roles,
            True
        )
        # print(checks)
        return checks[name]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if str(message.channel.type) != 'text':
            return
        await handle_message(message)
        author = message.author

        failed_checks = []

        guild = message.guild

        for check in checks:
            failed = False

            channel = message.channel
            enabled = await self.check_enabled(
                guild,
                check.name,
                channel,
                author
            )
            if enabled:

                failed = await check.check(message)
                if failed:

                    failed_checks.append(check.check_name)

        if failed_checks != []:
            await handle_infractions(message, failed_checks)
            author = message.author
            if len(failed_checks) > 1:

                desc = '**Infractions:**\n'
                for check in failed_checks:
                    desc += f'> **•** `{check}`\n'
            else:

                check = failed_checks[0]
                desc = f'<@{author.id}>\'s message was deleted because it failed the following check: `{check}`'
            fields = [('**Message Content**', message.content)]
            await log(
                message,
                desc,
                showauth=True,
                fields=fields
            )

            await message.delete()

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        if 'guild_id' not in payload.data:
            return
        guild = self.bot.get_guild(int(payload.data['guild_id']))

        channel = guild.get_channel(int(payload.data['channel_id']))

        message = await channel.fetch_message(int(payload.data['id']))
        if message.author == self.bot.user:
            return

        if str(message.channel.type) == 'text':
            failed_checks = []
            for check in checks:
                failed = False

                enabled = await self.check_enabled(
                    guild,
                    check.name,
                    channel,
                    await guild.fetch_member(payload.data['author'])
                )
                if enabled:

                    failed = await check.check(message)
                    if failed:

                        failed_checks.append(check.check_name)

            if failed_checks != []:
                await handle_infractions(message, failed_checks)
                author = message.author
                if len(failed_checks) > 1:

                    desc = f'<@{author.id}>\'s message was automatically deleted.\n**Infractions:**\n'
                    for check in failed_checks:
                        desc += f'> **•** `{check}`\n'
                else:

                    check = failed_checks[0]
                    desc = f'<@{author.id}>\'s message was deleted because it failed the following check: `{check}`'
                fields = [('**Message Content**', message.content)]
                await log(
                    message,
                    desc,
                    showauth=True,
                    fields=fields
                )
                await message.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_id = payload.guild_id
        banned_reactions = await read('banEmojis', decrypt=False)
        if guild_id in banned_reactions:
            if payload.emoji in banned_reactions[guild_id]:

                guild_id = payload.guild_id
                channel_id = payload.channel_id
                guild = self.bot.get_guild(guild_id)
                msg_id = payload.message_id

                channel = guild.get_channel(channel_id)
                msg = await channel.fetch_message(msg_id)
                reactions = msg.reactions
                for r in reactions:
                    if r.emoji == payload.emoji:
                        for user in r.users:
                            r.remove(user)
                            handle_banned_emoji(r, user)

    @commands.command(name='listchecks', aliases=['lc'])
    async def guild_checks(self, ctx, channel: discord.TextChannel = None):
        '''List enabled and disabled checks.
        Example Usage:
        ``````css
        ?lc // Gets the defalt checks for the server.
        ``````css
        ?lc #​channel // Get checks in #​channel
        ```
        '''
        guild = ctx.guild

        if channel is None:
            channel = ctx.channel

        desc = '```css\n'

        for check in checks:

            enabled = await self.check_enabled(guild, check.name, channel)

            name = check.check_name

            name += ':'
            name = name.ljust(30, ' ')
            if enabled:
                name.ljust
                desc += name + '✅\n'

            else:
                desc += name + '❌\n'
        desc += '```'
        await ctx.send(desc)


def setup(bot):

    bot.add_cog(Checks(bot))
