import sys
import asyncio
import discord
import datetime
import time
import traceback
from tools.read_write import read, write
from utils import get_muted_role, error_log
from Moderation.spamchart import check_expire


async def log(text, guild, title='Automatic'):

    log_embed = discord.Embed(
        title=title,
        description=text,
        color=0x00e0f5
    )

    log_dict = await read('al')

    try:
        action_log_id = log_dict[guild.id]
        # print(action_log_id)
        log_channel = discord.utils.get(guild.text_channels, id=action_log_id)
        await log_channel.send(embed=log_embed)
    except KeyError:
        pass
    except AttributeError:
        pass


async def check_ban():
    global bot
    banList = await read('banList')
    delList = []
    for guild_list in banList:
        for userId in banList[guild_list]:
            date = banList[guild_list][userId]
            date = datetime.datetime.strptime(date, "%Y-%m-%w-%W %H:%M:%S")
            if datetime.datetime.now() >= date:
                delList.append([guild_list, userId])

    for a in delList:
        guild = bot.get_guild(a[0])
        banEntry = await guild.bans()
        for each in banEntry:
            if each.user.id == a[1]:
                user = each.user
                break
        if not user:
            # print(f'user {a[1]} not found')
            return
        # print('unbanning')
        username = user.display_name
        await log(
            f'`{username}` has been unbanned because their time is up',
            guild
        )
        await guild.unban(user=user, reason='User\'s time was up')
        del banList[a[0]][a[1]]

    await write('banList', banList)


async def check_mute():
    global bot
    mute_list = await read('muteList')
    del_list = []
    for guild_list in mute_list:
        for user_id in mute_list[guild_list]:
            date = mute_list[guild_list][user_id]
            date = datetime.datetime.strptime(date, "%Y-%m-%w-%W %H:%M:%S")
            if datetime.datetime.now() >= date:
                del_list.append([guild_list, user_id])

    for a in del_list:
        guild = bot.get_guild(int(a[0]))
        member_id_list = [member.id for member in guild.members]
        if int(a[1]) not in member_id_list:
            del mute_list[a[0]][a[1]]
            continue

        user = guild.get_member(int(a[1]))
        username = user.display_name
        await log(
            f'`{username}` has been unmuted because their mute duration has ended.',
            guild
        )
        del mute_list[a[0]][a[1]]
        await user.remove_roles(await get_muted_role(guild))

    await write('muteList', mute_list)


async def spam_chart_daemon(bot):
    while True:
        #print("Clearing spamchart")
        try:
            await check_expire()
        except Exception as e:
            traceback_message = traceback.format_exc()
            out = sys.exc_info()

            print(traceback_message)
            print('\n\\nn' + '>' * 20 + '\nTRACEBACK_MSG\n\n\n',
                  traceback_message, '\n<' * 20, '\n\n\n')
            print('\n\\nn' + '>' * 20 + '\nOUT\n\n\n',
                  out, '\n<' * 20, '\n\n\n')
            print('\n\\nn' + '>' * 20 + '\nE\n\n\n', e, '\n<' * 20, '\n\n\n')

        await asyncio.sleep(1)


async def bg_tasks(client):
    global bot
    bot = client
    tasks = [
        check_ban,
        check_mute,
    ]
    while True:
        # print('Running tasks')
        for task in tasks:
            try:
                await task()
            except Exception as e:

                traceback_message = traceback.format_exc()
                out = sys.exc_info()
                await error_log(traceback_message, out, bot)
                print(e)
        await asyncio.sleep(1)
