package checks

import (
	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/util/perms"
)

// IsGuild is a check that checks if the mssage was sent in a guild
func IsGuild(m *discordgo.Message) bool {
	return m.GuildID != ""
}

// HasPermissions is a basic permission check for discord and asb perm checks
func HasPermissions(s **discordgo.Session, perm string, discordPerms ...perms.DiscordPermission) types.CheckFunc {
	return func(m *discordgo.Message) bool {
		fallback := perms.HasAnyPermissionsIn(*s, m, discordPerms...)
		hasPerms, _ := perms.HasPermission(*s, m, perm, fallback)

		return hasPerms
	}
}

// HasPermission checks to see if a user has an asb perm
func HasPermission(s **discordgo.Session, perm string, fallback bool) types.CheckFunc {
	return func(m *discordgo.Message) bool {
		hasPerm, _ := perms.HasPermission(*s, m, perm, fallback)

		return hasPerm
	}
}
