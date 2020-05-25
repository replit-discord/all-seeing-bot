import io
import sys
import discord
import traceback
import json
from datetime import datetime
from discord.ext import commands
from utils import is_dev, execute
from contextlib import redirect_stdout
from tools.read_write import read, write


class DevCommands(commands.Cog, name='dev'):
    '''Developer only commands'''

    def __init__(self, bot):
        self.bot = bot
        self.color = 0x267d1d

    def cog_check(self, ctx):
        return is_dev(ctx)

    def check(self, ctx):
        return is_dev(ctx)

    def generate_embed(self, title, description, color=0x00ff22):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        embed.timestamp = datetime.now()
        return embed

    @commands.command(name='write', aliases=['w'])
    async def Write(self, ctx, path: str, data: str, encrypt: bool = True):
        await write(path, data, encrypt)

    @commands.command(name='read', aliases=['r'])
    async def Read(
            self,
            ctx,
            path: str,
            evaluate: bool = True,
            decrypt: bool = True
    ):
        data = json.dumps(await read(path, evaluate, decrypt))

        embed = self.generate_embed(f'**{path}**', f'```json\n{data}```')
        await ctx.send(embed=embed)

    @commands.command(name='exec', aliases=['execute'])
    async def Execute(self, ctx, *_):
        author = ctx.author

        msg = ctx.message
        try:
            f = io.StringIO()
            with redirect_stdout(f):
                command = msg.content.split(None, 1)[1]

                await execute(command, locals())
            out = f.getvalue()
            done_oof = False
        except Exception:

            traceback_message = traceback.format_exc()
            out = sys.exc_info()
            done_oof = True
        if out != '':
            if not done_oof:
                await msg.channel.send(
                    embed=discord.Embed(
                        title='Unsafe Eval',
                        description=out
                    )
                )
            else:

                e_type, e_msg = str(out[0])[8:][:-2], traceback_message
                await msg.channel.send(
                    embed=discord.Embed(
                        title=f"**{e_type}**",
                        description=f'```py\n{e_msg}\n```',
                        color=0xff0000
                    ).set_footer(text='Uh oh, you made an oopsie!')
                )
        else:
            await msg.channel.send('Task completed')

    @commands.command(name='reload')
    async def mod_reload(self, ctx, module: str):
        extensions = self.bot.extensions
        if module == 'all':
            for extension in extensions:
                self.bot.unload_extension(module)
                self.bot.load_extension(module)
            await ctx.send('Done')
        if module in extensions:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
            await ctx.send('Done')
        else:
            await ctx.send('Unknown Module')

    @commands.command(name='load')
    async def mod_load(self, ctx, module: str):
        try:
            self.bot.load_extension(module)
            await ctx.send('Done')
        except commands.errors.ExtensionNotFound:
            await ctx.send(f'Could not load module: `{module}`')
        except commands.errors.NoEntryPointError:
            await ctx.send('No setup command in `{module}.py` stupid!')

    @commands.command(name='unload')
    async def mod_unfload(self, ctx, module: str):
        try:
            self.bot.unload_extension(module)
            await ctx.send('Done')
        except commands.errors.ExtensionNotLoaded:
            await ctx.send(
                f'Could not unload module: `{module}` because'
                ' it was not loaded'
            )

    @commands.command(name='listextensions', aliases=['le'])
    async def list_extensions(self, ctx):
        extensions_dict = self.bot.extensions
        msg = '```css\n'

        extensions = []

        for b in extensions_dict:
            print(b)
            extensions.append(b)

        for a in range(len(extensions)):
            msg += f'{a}: {extensions[a]}\n'

        msg += '```'
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(DevCommands(bot))
