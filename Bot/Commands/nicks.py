import discord
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands
from utils import get_muted_role, perm_cache
from tools.read_write import read, write
from utils import find_date, InvalidDate, update
from random import randint


def get_embed(user: discord.Member, nick: str) -> discord.Embed:
    emb = discord.Embed(
        title='**Nickname Requested**',
        description=f'<@{user.id}> would like to have their nickname set to `{nick}`'
    )

    emb.timestamp = datetime.utcnow()

    return emb


class Nicks(commands.Cog, name='nicks'):
    '''Moderation Commands'''

    bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color = 0x32a889

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        return True

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if not payload.guild_id:
            return
        data = await read('nick_stuff')
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        if str(guild.id) not in data:
            return
        guild_data = data[str(guild.id)]
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        if 'users' not in guild_data:
            return

        if not 'mod_channel' in guild_data or guild_data['mod_channel'] != payload.channel_id:
            return

        for user in guild_data['users']:
            if guild_data['users'][user]['message'] == payload.message_id:
                member = await self.bot.fetch_user(user)
                await member.send('Your nickname request has expired, please use requestnick again.')
                break

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id:
            return
        data = await read('nick_stuff')
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        if str(guild.id) not in data:
            return
        guild_data = data[str(guild.id)]
        if payload.user_id == self.bot.user.id:
            return
        if 'users' not in guild_data:
            return
        if not 'mod_channel' in guild_data or guild_data['mod_channel'] != payload.channel_id:
            return

        member = None
        for user in guild_data['users']:
            if guild_data['users'][user]['message'] == payload.message_id:
                member = await guild.fetch_member(user)
                break
        if not member:
            return
        nickname = guild_data['users'][str(member.id)]['nick']
        channel = guild.get_channel(payload.channel_id)

        emoji = str(payload.emoji)
        if not emoji == '✅' and not emoji == '❌':
            return

        message = await channel.fetch_message(payload.message_id)
        if emoji == '✅':
            await member.edit(nick=nickname)
            await member.send('Your nickname request has been approved.')
        else:
            await member.send('Your nickname request has been denied.')

        await message.delete()

        del data[str(guild.id)]['users'][str(member.id)]

        await write('nick_stuff', data)

    @commands.command(name='modnickchannel', aliases=['mnc'])
    async def set_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        fd = await read('nick_stuff')
        guild = ctx.guild

        if str(guild.id) in fd:
            guild_data = fd[str(guild.id)]
        else:
            guild_data = {}

        guild_data = update(guild_data, {'mod_channel': channel.id})

        fd[str(guild.id)] = guild_data

        await write('nick_stuff', fd)

        await ctx.send(f'channel set to <#{channel.id}>')

    @commands.command(name='requestnick', aliases=['iwannanickpleasenickme'])
    async def request_nick(self, ctx: commands.Context, *args):
        nick = ' '.join(args)
        guild = ctx.guild

        fd = await read('nick_stuff')

        channel: discord.TextChannel = None
        message: discord.Message = None

        if str(guild.id) in fd:
            guild_data = fd[str(guild.id)]
            if 'mod_channel' in guild_data:
                channel = ctx.guild.get_channel(guild_data['mod_channel'])
            if 'users' in guild_data and channel != None:
                users = guild_data['users']
                if str(ctx.author.id) in users:
                    user_data = users[str(ctx.author.id)]

        if not channel:
            await ctx.author.send('nick requests have not been setup yet')

        message = await channel.send(embed=get_embed(ctx.author, nick,), delete_after=10)

        await message.add_reaction('✅')
        await message.add_reaction('❌')

        data = {
            str(ctx.guild.id): {
                'users': {
                    str(ctx.author.id): {
                        'nick': nick,
                        'user_id': ctx.author.id,
                        'message': message.id,
                    }
                }
            }
        }

        fd = update(fd, data)
        await write('nick_stuff', fd)

        await ctx.author.send('Nick requested')


def setup(bot):
    bot.add_cog(Nicks(bot))
