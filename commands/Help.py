import discord

from commands import data_tweaking

main_help = discord.Embed(title='Help', description='''
**lol i need something to put here,**''')
main_help.set_footer(text='Use help <catagory> to get help on a certain section.')
mod_help = discord.Embed(title='Help', description='''
**Customization:** Customization commands, such as mute duration''', color=0xff8000)
mod_help.set_footer(text='Use help <catagory> to get help on a certain section.')
modPgs = {
    'customization': data_tweaking.helpMsg
    }
mainPgs = {}


async def Help(args, msg):
    print(msg.author.guild_permissions.administrator)
    if '' in args:
        args.remove('')
    channel = msg.channel
    if msg.author.guild_permissions.administrator:
        if len(args) == 0:
            await channel.send(embed=mod_help)
        elif len(args) == 1:
            if args[0].lower() in modPgs:
                await channel.send(embed=modPgs[args[0].lower()])
            else:
                await channel.send(args[0].lower() + ' is not in the help list.')
        else:
            await channel.send('Invalid ammount of args. example command: `help Customization`')
    if not msg.author.guild_permissions.administrator:
        if len(args) == 0:
            await channel.send(embed=main_help)
        elif len(args) == 1:
            if args[0].lower() in mainPgs:
                await channel.send(embed=mainPgs[args[0].lower()])
            else:
                await channel.send(args[0].lower() + ' is not in the help list.')
        else:
            await channel.send('Invalid ammount of args. example command: `help Customization`')
