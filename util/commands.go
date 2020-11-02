package util

import (
	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/util/perms"
)

// IsAdmin returns whether the author of a message is an admin or not
func IsAdmin(s *discordgo.Session, m *discordgo.Message) bool {
	permissions, err := s.State.UserChannelPermissions(m.Author.ID, m.ChannelID)

	if err != nil {
		return false
	}

	return permissions&int(perms.Administrator) > 0
}

// HasAnyPermissionsIn returns whether the author of a message has the permissions listed.
func HasAnyPermissionsIn(s *discordgo.Session, m *discordgo.Message, permissionNodes ...perms.DiscordPermission) bool {
	permissions, err := s.State.UserChannelPermissions(m.Author.ID, m.ChannelID)

	if err != nil {
		return false
	}

	var requiredPerms = 0

	for _, perm := range permissionNodes {
		requiredPerms |= int(perm)
	}

	return permissions&requiredPerms > 0
}
