import commands
cmdDict = {
    'muteduration': commands.data_tweaking.set_duration,
    'offenseduration': commands.data_tweaking.offense_time,
    'offenselimit': commands.data_tweaking.offense_limit,
    'help': commands.Help.Help,
    'reset': commands.data_tweaking.reset,
    'read': commands.data_tweaking.Read,
    'write': commands.data_tweaking.Write,
    'ban': commands.moderation_tools.ban,
    'unban': commands.moderation_tools.unban
    }
