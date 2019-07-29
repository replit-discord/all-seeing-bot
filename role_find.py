import discord

async def get_muted_role(guild):
    muted_role = discord.utils.get(guild.roles, name='Muted')
    if muted_role is None:
        muted_permissions = discord.Permissions()
        muted_permissions.send_messages = False
        muted_permissions.add_reactions = False
        muted_role = await guild.create_role(
            name='Muted',
            permissions=muted_permissions,
            color=discord.Color.dark_red()
        )

    return muted_role