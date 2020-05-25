import discord
import json
from datetime import datetime
from discord.ext import commands


class HelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__(command_attrs={
            'help': 'Displays the help message for commands.'})

    async def prepare_help_command(self, ctx, command=None):
        if not command:
            await super().prepare_help_command(ctx)
            return
        else:
            await super().prepare_help_command(ctx, command.lower())

    def get_command_signature(self, command):
        params = command.clean_params
        args = ' '.join([f'<{a}>' for a in params if a != 'argv'])
        return '{0.clean_prefix}{1.qualified_name} {2}'.format(self, command, args)

    async def send_command_help(self, command):

        desc = self.get_command_signature(command)
        desc += '\n' + command.help.replace('?', self.clean_prefix)
        embed = discord.Embed(
            title=command.qualified_name,
            description=desc,
            color=command.cog.color
        )
        destination = self.get_destination()
        await destination.send(embed=embed)

    def get_bot_mapping(self):

        return super().get_bot_mapping()

    async def send_bot_help(self, mapping):
        cogs = []

        for cog in unfiltered_cogs:
            commands = await self.filter_commands(cog.get_commands())

            if commands != [] and cog.qualified_name != 'Help':
                cogs.append(cog)
        embed = discord.Embed(
            title='Help',
            color=0xebf2ff
        )
        prefix = self.clean_prefix
        for cog in cogs:
            embed.add_field(
                name=f'**{cog.qualified_name.upper()}**',
                value=f'{cog.description}',
                inline=True
            )
        embed.timestamp = datetime.now()
        embed.set_footer(
            text=f'Use {prefix}help <category> to get that category\'s commands'
        )
        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_cog_help(self, cog):

        commands = cog.get_commands()
        commands = await self.filter_commands(commands)
        desc = f'Commands you can use in `{cog.qualified_name}`:'
        for command in commands:
            desc += '\n\n**{0.clean_prefix}{1.name}**: *{1.short_doc}*'.format(
                    self,
                    command
            )
        destination = self.get_destination()
        if commands is []:
            await destination.send('You can\'t use any commands in this category')
        embed = discord.Embed(
            title=f'**{cog.qualified_name.title()}**',
            description=desc,
            color=cog.color
        )
        await destination.send(embed=embed)


class Help(commands.Cog, name='help'):
    '''Help Command'''

    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()

        bot.help_command.cog = self
        self.color = 0xebf2ff

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
