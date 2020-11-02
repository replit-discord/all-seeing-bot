package commands

import (
	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"github.com/repl-it-discord/all-seeing-bot/util"
	"github.com/repl-it-discord/all-seeing-bot/util/perms"
)

func mute(
	s *discordgo.Session,
	m *discordgo.MessageCreate,
	config *db.GuildConfigType,
	command string,
	args *string,
) *string {
	// ensure perms and write commands. parseduration handy
	var out string

	hasPerm, _ := perms.HasPermission(s, m.Message, "mute", false)

	if hasPerm && !util.HasAnyPermissionsIn(s, m.Message, perms.Administrator, perms.ManageRoles, perms.ManageMessages) {
		out = "You do not have permission to do this"
		return &out
	}

	return &out
}
