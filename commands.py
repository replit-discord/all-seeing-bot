import discord

ADMINS = [
    487258918465306634
    ]

GUILDS = [
    437048931827056642
    ]


async def evaluate(ctx, args):
    message = ctx['message']
    code = ' '.join(args)

    if ctx['guild'].id in GUILDS and ctx['author'].guild_permissions.administrator or ctx['author'].id in ADMINS:
        try:
            await channel.send(eval(code))
        except discord.errors.HTTPException:
            await channel.send('Task completed')

        return
