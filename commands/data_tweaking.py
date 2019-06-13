import os
import discord

import asyncio
from  rw import read, write
from findTime import findTime

async def set_duration(args, msg):
    if msg.author.guild_permissions.administrator:
        guild = msg.guild
        bot_prefix = await read('bot_prefix', False) 
        prefix_length = len(bot_prefix)
        fdl = await read('duration')
        oT = (await read('od'))[guild.id]
        if findTime(args[0]) > oT:
            fdl[guild.id] = findTime(args[0])
            await write('duration', fdl)
            
            await msg.channel.send('Mute duration has been set.')
        else:
            await msg.channel.send(f'Mute duration cannot last less time then offense duration (Seconds: `{str(oT)}`)!')

async def offense_time(args, msg):
    if msg.author.guild_permissions.administrator:
        guild = msg.guild
        bot_prefix = await read('bot_prefix', False) 
        prefix_length = len(bot_prefix)
        od = await read('duration')
        mT = (await read('duration'))[guild.id]
        if not findTime(args[0]) < mT:
            od[guild.id] = findTime(args[0])
            await write('od', od)
            await msg.channel.send('Offense duration has been set.')
        else:
            await msg.channel.send(f'Offense duration cannot be longer than mute time (Seconds: `{str(mT)}`)!')
