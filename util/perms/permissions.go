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

var permissionMap = []string{
	"getconfig",
	"updateconfig",
	"mute",
}

// Permissions is a type used to store permission data in a byte array
type Permissions []byte

// GetPermission gets the bits for a permission
func (p *Permissions) GetPermission(perm string) byte {
	var bitPos int
	found := false

	for i, v := range permissionMap {
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

// HasPermission gets whether a member has permission to perform an action or not.
func HasPermission(s *discordgo.Session, m *discordgo.Message, perm string, fallback bool) (bool, error) {
	db.SetGuildPermissions("585606083897458691", nil, nil, []byte{0b101010})
	var userRoles []*discordgo.Role

	perms, err := db.GetGuildPermissions(m.GuildID)

	if err != nil {
		return false, err
	}

	hasRole := func(roleID string) bool {
		if roleID == m.GuildID {
			return true
		}
		for _, v := range userRoles {
			if v.ID == roleID {
				return true
			}
		}

		return false
	}

	guild, err := s.State.Guild(m.GuildID)

	if err != nil {
		return false, err
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

	for _, p := range *perms {
		pV := Permissions(p.Permissions)
		if p.ChannelID == "" {
			if hasRole(p.RoleID) {
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

	if permVal&0x2 > 0 {
		return permVal&0x1 > 0, nil
	}

	return fallback, nil

}
