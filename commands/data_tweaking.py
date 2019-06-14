import discord
from at import argTest

from findTime import findTime
from rw import read, write

helpMsg = discord.Embed(title='Customization', description='''
**`muteduration <time>`:**  Sets the base mute duration.
**`offenseduration <time>`:**  Sets how long an offense/msg for spam count lasts. 
**`offenselimit <ammount>`:**  Sets how many offenses a user can make before being muted.
''', color=0x00ff80)


async def set_duration(args, msg):
    args.remove('')
    if msg.author.guild_permissions.administrator:
        types = [
            float
            ]

        if not len(args) == 0:
            try:
                args[0] = findTime(args[0])
                if len(args) == 1 and argTest(types, args):
                    guild = msg.guild
                    fdl = await read('duration')
                    oT = (await read('od'))[guild.id]
                    if findTime(args[0]) > oT:
                        fdl[guild.id] = findTime(args[0])
                        await write('duration', fdl)

                        await msg.channel.send('Mute duration has been set.')
                    else:
                        await msg.channel.send(
                            f'Mute duration cannot last less time then offense duration (Seconds: `{str(oT)}`)!')
                elif len(args) != 1:

                    command = msg.content.lower().split(' ')[0]
                    await msg.channel.send(f'Invalid ammount of args. Example command: `{command} 5s`')
                elif not argTest(types, args):
                    command = msg.content.lower().split(' ')[0]
                    await msg.channel.send(f'Invalid arg types. Example command: `{command} 5s`')
            except ValueError:
                await msg.channel.send(f'Invalid arg type. Arg needs to be a time. Example command: `{command} 5s`')
        else:
            cd = (await read("duration"))[msg.guild.id]
            await msg.channel.send(f'Current offense duration is `{cd}`')


async def offense_time(args, msg):
    args.remove('')
    if msg.author.guild_permissions.administrator:

        types = [
            float
            ]

        if not len(args) == 0:
            try:
                args[0] = findTime(args[0])
                if len(args) == 1 and argTest(types, args):
                    guild = msg.guild
                    od = await read('od')
                    mT = (await read('od'))[guild.id]
                    if not args[0] < mT:
                        od[guild.id] = args[0]
                        await write('od', od)
                        await msg.channel.send('Offense duration has been set.')
                    else:
                        await msg.channel.send(f'Offense duration cannot be longer than mute time (Seconds: `{str(mT)}`)!')
                elif len(args) != 1:

                    command = msg.content.lower().split(' ')[0]
                    await msg.channel.send(f'Invalid ammount of args. Example command: `{command} 5s`')
                elif not argTest(types, args):
                    command = msg.content.lower().split(' ')[0]
                    await msg.channel.send(f'Invalid arg types. Example command: `{command} 5s`')
            except ValueError:
                await msg.channel.send(f'Invalid arg type. Arg needs to be a time. Example command: `{command} 5s`')
        else:
            cd = (await read("od"))[msg.guild.id]
            await msg.channel.send(f'Current offense duration is `{cd}`')


async def offense_limit(args, msg):
    try:
        args.remove('')
    except ValueError:
        print('oof', args)
    print(args)
    if msg.author.guild_permissions.administrator:
        types = [
            int
            ]

        if not len(args) == 0:
            try:
                args[0] = int(args[0])
                if len(args) == 1 and argTest(types, args):
                    guild = msg.guild
                    od = await read('ol')

                    od[guild.id] = args[0]
                    await write('ol', od)
                    await msg.channel.send('Offense limit has been set.')

                elif len(args) != 1:

                    command = msg.content.lower().split(' ')[0]
                    await msg.channel.send(f'Invalid ammount of args. Example command: `{command} 5`')
                elif not argTest(types, args):
                    command = msg.content.lower().split(' ')[0]
                    await msg.channel.send(f'Invalid arg types. Example command: `{command} 5`')
            except IndexError:
                command = msg.content.lower().split(' ')[0]
                await msg.channel.send(f'Invalid arg types. Example command: `{command} 5`')
        else:
            cd = (await read("ol"))[msg.guild.id]
            await msg.channel.send(f'Current offense limit is `{cd}`')


async def reset(args, msg):
    if msg.author.id == 487258918465306634:
        try:
            await read(args[0])
            if len(args) == 1:
                await write(args[0], {})
            elif len(args) == 2:
                await write(args[0], args[1])
            else:
                await msg.channel.send('Invalid argument ammount')
        except ValueError:
            pass
    else:
        await msg.channel.send('Only the bot owner can use this command!')


async def Read(args, msg):
    if msg.author.id == 487258918465306634:
        if len(args) == 1:
            rMessage = await read(args[0])
        elif len(args) == 2:
            rMessage = await read(args[0], eval(args[1]))
        elif len(args) == 3:
            rMessage = await read(args[0], eval(args[1]), eval(args[2]))
        else:
            rMessage = 'Invalid ammount of args'
        await msg.channel.send(rMessage)
    else:
        await msg.channel.send('Only the bot owner can use this command!')


async def Write(args, msg):
    if msg.author.id == 487258918465306634:
        if len(args) == 2:
            await write(args[0], args[1])
            rMessage = 'Task Complete'
        elif len(args) == 3:
            await write(args[0], args[1], eval(args[2]))
            rMessage = 'Task Complete'
        else:
            rMessage = 'Invalid ammount of args'

        await msg.channel.send(rMessage)

    else:
        await msg.channel.send('Only the bot owner can use this command!')
