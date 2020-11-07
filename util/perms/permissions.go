package perms

import (
	"fmt"
	"math"
	"sort"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/db"
)

// DiscordPermission is a bit mask for a discord permission
type DiscordPermission int

// Bit values for discord permissions
const (
	CreateInstantInvite = 1 << iota
	KickMembers
	BanMembers
	Administrator
	ManageChannels
	ManageGuild
	AddReactions
	ViewAuditLog
	PrioritySpeaker
	Stream
	ViewChannel
	SendMessages
	SendTtsMessages
	ManageMessages
	EmbedLinks
	AttachFiles
	ReadMessageHistory
	MentionEveryone
	UseExternalEmojis
	ViewGuildInsights
	Connect
	Speak
	MuteMembers
	DeafenMembers
	MoveMembers
	UseVad
	ChangeNickname
	ManageNicknames
	ManageRoles
	ManageWebhooks
	ManageEmojis
)

var permissions = []string{
	"mute",
	"unmute",
	"prefix",
	"setloggerchannel",
}

// Permissions is a type used to store permission data in a byte array
type Permissions []byte

// GetPermission gets the bits for a permission
func (p *Permissions) GetPermission(perm string) byte {
	var bitPos int
	found := false

	for i, v := range permissions {
		if v == perm {
			bitPos = 2 * i
			found = true
			break
		}
	}

	if !found {
		panic(fmt.Errorf("Unknown permission: %s", perm))
	}

	byteIndex := int(math.Floor(float64(bitPos) / 8))

	if byteIndex >= len(*p) {
		return 0
	}

	return (*p)[byteIndex] >> uint8(bitPos%8) & 0x3
}

// HasAnyPermissionsIn returns whether the author of a message has the permissions listed.
func HasAnyPermissionsIn(s *discordgo.Session, m *discordgo.Message, permissionNodes ...DiscordPermission) bool {
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

// HasPermission gets whether a member has permission to perform an action or not.
func HasPermission(s *discordgo.Session, m *discordgo.Message, perm string, fallback bool) (bool, error) {
	var userRoles []*discordgo.Role

	perms, err := db.GetGuildPermissions(m.GuildID)

	if err != nil {
		return fallback, err
	}

	guild, err := s.State.Guild(m.GuildID)

	if err != nil {
		return fallback, err
	}

	for _, roleID := range m.Member.Roles {
		for _, role := range guild.Roles {
			if role.ID == roleID {
				userRoles = append(userRoles, role)
			}
		}
	}

	sort.Slice(userRoles[:], func(i, j int) bool {
		return userRoles[i].Position < userRoles[j].Position
	})

	permVal := byte(0)

	for _, p := range perms {
		if p.RoleID != m.GuildID {
			continue
		}
		pV := Permissions(p.Permissions)

		if p.ChannelID == "" {
			if p.RoleID == m.GuildID {
				if pV.GetPermission(perm)&0x2 > 0 {
					if pV.GetPermission(perm)&0x1 > 0 {
						permVal = 0x3
					} else {
						permVal = 0x2
					}
				}
			}
		}
	}

	for _, p := range perms {
		if p.RoleID != m.GuildID {
			continue
		}
		pV := Permissions(p.Permissions)

		if p.ChannelID == m.ChannelID {
			if p.RoleID == m.GuildID {
				if pV.GetPermission(perm)&0x2 > 0 {
					if pV.GetPermission(perm)&0x1 > 0 {
						permVal = 0x3
					} else {
						permVal = 0x2
					}
				}
			}
		}
	}

	for _, r := range userRoles {
		for _, p := range perms {
			if p.RoleID != r.ID || p.ChannelID != "" {
				continue
			}
			pV := Permissions(p.Permissions)

			if pV.GetPermission(perm)&0x2 > 0 {
				if pV.GetPermission(perm)&0x1 > 0 {
					permVal = 0x3
				} else {
					permVal = 0x2
				}
			}
		}

		for _, p := range perms {
			if p.RoleID != r.ID || p.ChannelID != p.ChannelID {
				continue
			}
			pV := Permissions(p.Permissions)

			if pV.GetPermission(perm)&0x2 > 0 {
				if pV.GetPermission(perm)&0x1 > 0 {
					permVal = 0x3
				} else {
					permVal = 0x2
				}
			}
		}
	}

	if permVal&0x2 > 0 {
		return permVal&0x1 > 0, nil
	}

	return fallback, nil

}
