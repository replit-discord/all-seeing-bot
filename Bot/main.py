import os
import sys
import discord
import asyncio
#import webserver
from discord.ext import commands
from background_tasks import bg_tasks, spam_chart_daemon
from utils import check_command, is_dev
import importlib

intents = discord.Intents.all()


async def determine_prefix(bot, message):
    if message.guild and message.guild.id == 437048931827056642:
        return "$"
    return "?"

bot = commands.Bot(
    command_prefix=determine_prefix,
    case_insensitive=True,
    intents=intents
)


# regex to find most print statements \n\s*print\([^()]*\)
class initialized:
    def __init__(self):
        self.started = False

    def __call__(self):
        if not self.started:
            self.started = True
            return False
        else:
            return True


started = initialized()

extensions = [
    'Commands.dev_cmds',
    'Commands.data_tweaking',
    # 'Other.Starboard.main',
    'Commands.nicks',
    'Commands.moderation',
    'Moderation.main',
    'Commands.fun',
    'Commands.help',
    # 'Mail.main',
    'Other.logger'
]

converter = commands.RoleConverter()


def testFunc(ctx: commands.Context) -> bool:
    return ctx.guild.id == 437048931827056642


@bot.command(name="helper")
@commands.check(testFunc)
async def toggle_helper_role(ctx: commands.Context, name: str):
    try:
        role = await converter.convert(ctx, f'help-{name}')
    except commands.errors.BadArgument:
        await ctx.send("nope nope doesnt exist nice try")
        return

    if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
    else:
        await ctx.author.add_roles(role)

    await ctx.send('done')


if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    bot.add_check(check_command)
    await bot.change_presence(
        activity=discord.Activity(
            name='everything', type=discord.ActivityType(3)
        )
    )
    # print(len(bot.commands))
    if not started():
        bot.loop.create_task(spam_chart_daemon(bot))
        bot.loop.create_task(bg_tasks(bot))

    # print('ready')


@bot.event
async def on_command_error(ctx, error):
    if type(error) == commands.errors.CheckFailure:
        # await ctx.message.delete()
        msg = await ctx.send(f"You cant use `{ctx.prefix}{ctx.command}` here...")
        await asyncio.sleep(3)
        await msg.delete()
    else:
        raise error

# webserver.keep_alive(bot)
token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)
