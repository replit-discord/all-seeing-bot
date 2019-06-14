import datetime

from rw import read, write


def findDate(string):
    now = datetime.datetime.now()
    strNow = datetime.datetime.now().strftime("%Y-%m-%w-%W %H:%M:%S")
    timeTypes = [
        'd',
        'm',
        'w',
        's',
        'h'
        ]
    date = strNow[:13].split('-')
    time = strNow[14:].split(':')
    if string[-1] == 'm':
        date[1] = str(now.month + int(string[:-1]))

    elif string[-1] == 'd':
        date[2] = str(now.day + int(string[:-1]))

    elif string[-1] == 'w':
        date[3] = str(now.week + int(string[:-1]))

    elif string[-1] == 's':
        time[2] = str(now.second + int(string[:-1]))
    # derp
    elif string[-1] == 'h':
        time[0] = str(now.hour + int(string[:-1]))

    if string[-1] in timeTypes:
        try:
            while int(time[2]) > 59:
                time[2] = str(time[2] - 60)
                time[1] = str(time[1] - 60)
            while int(time[1]) > 59:
                time[1] = str(time[1] - 60)
                time[0] = str(time[0] - 60)
            while int(time[0]) > 23:
                time[0] = str(time[0] - 24)
                date[2] = str(time[2] - 24)
            while int(date[2]) > 6:
                date[0] = str(date[0] - 7)
                date[3] = str(date[3] - 7)
            while int(date[3]) > 51:
                date[3] = str(date[2] - 52)
                date[0] = str(date[0] - 52)
            while int(date[1]) > 11:
                date[1] = str(date[1] - 12)
                date[0] = str(date[0] - 12)

            newDate = '-'.join(date) + ' ' + ':'.join(time)
            return str(newDate)
        except:
            pass


    else:
        try:
            newDate = now.day + int(string)
            return newDate
        except:
            return False


async def ban(args, msg):
    if msg.author.guild_permissions.administrator:
        channel = msg.channel
        guild = msg.guild
        if len(args) > 1:
            date = findDate(args[1])
        else:
            date = False
        banUserId = msg.mentions[0].id
        if date != False:
            bl = (await read('banList'))
            if guild.id not in bl:
                bl[guild.id] = {}
            bl[guild.id][banUserId] = date = str(date)
            await write('banList', bl)
            if len(args) > 2:
                reason = args[2:].join(' ')
                await guild.ban(user=guild.get_member(banUserId), reason=reason)
                await channel.send('User has been banned')
            else:
                await guild.ban(user=guild.get_member(banUserId))
                await channel.send('User has been banned')
        else:
            if len(args) > 1:
                reason = ' '.join(args[1:])
                await guild.ban(user=guild.get_member(banUserId), reason=reason)
                await channel.send('User has been banned')
            else:
                await guild.ban(user=guild.get_member(banUserId))
                await channel.send('User has been banned')


    else:
        await msg.channel.send('You do not have permission to use this command')


async def unban(args, msg):
    if msg.author.guild_permissions.administrator:
        channel = msg.channel
        guild = msg.guild
        dispName = msg.author.display_name
        banLogs = await guild.bans()
        banIds = [y.user.id for y in banLogs]
        userId = int(args[0])
        banEntry = await guild.bans()
        if userId not in banIds:
            await channel.send('User is not banned!')

        else:
            for each in banEntry:
                if each.user.id == userId:
                    user = each.user
                    break
            if len(args) > 1:
                reason = ' '.join(args[:1])
                await guild.unban(user=user, reason=reason)
                await channel.send('User has been unbanned')
            else:
                await channel.send('User has been unbanned')
                await guild.unban(user=user, reason=dispName + ' unbanned him/her.')

        print('unbanning')

    else:
        await msg.channel.send('You do not have permission to use this command')
