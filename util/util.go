package util

import (
	"regexp"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"github.com/repl-it-discord/all-seeing-bot/util/perms"
)

// DevIDs is  a list of users with access to dev commands
var DevIDs = [...]string{"487258918465306634", "527937324865290260"}

// MentionRegex is the regex used to find mentions of any type
var MentionRegex *regexp.Regexp

// RoleMentionRegex is the regex used to find role mentions
var RoleMentionRegex *regexp.Regexp

// UserMentionRegex is the regex used to find user mentions
var UserMentionRegex *regexp.Regexp

// ChannelMentionRegex is the regex used to find user mentions
var ChannelMentionRegex *regexp.Regexp

// NumberRegex is just \d+
var NumberRegex *regexp.Regexp

// NonNumberRegex looks for any non-digit character
var NonNumberRegex *regexp.Regexp

var discriminatorRegex *regexp.Regexp

func init() {
	MentionRegex = regexp.MustCompile("<(@[!&])|(#)?\\d+>")
	RoleMentionRegex = regexp.MustCompile("<@&\\d+>")
	UserMentionRegex = regexp.MustCompile("<@!?\\d+>")
	ChannelMentionRegex = regexp.MustCompile("<#\\d+>")
	NumberRegex = regexp.MustCompile("\\d+")
	NonNumberRegex = regexp.MustCompile("[^\\d+]")
	discriminatorRegex = regexp.MustCompile("#\\d{4}")
}

// GetMutedRole returns the id of the server's muted role
func GetMutedRole(s *discordgo.Session, guildID string, config *db.GuildConfigType) (string, error) {
	if config == nil {
		var err error
		config, err = db.GetGuildConfig(guildID)

		if err != nil {
			return "", err
		}
	}

	if config.MuteRole != "" {
		return config.MuteRole, nil
	}

	guild, err := s.State.Guild(guildID)

	if err != nil {
		return "", err
	}

	for _, r := range guild.Roles {
		if strings.ToLower(r.Name) == "muted" {
			config.MuteRole = r.ID
			db.SetGuildConfig(guildID, config)

			return r.ID, nil
		}
	}

	r, err := s.GuildRoleCreate(guildID)

	if err != nil {
		return "", err
	}

	r.Name = "muted"

	for _, c := range guild.Channels {
		newPermissions := append(c.PermissionOverwrites, &discordgo.PermissionOverwrite{
			Type: "role",
			ID:   r.ID,
			Deny: perms.SendMessages | perms.AddReactions | perms.Connect | perms.Speak,
		})
		s.ChannelEditComplex(c.ID, &discordgo.ChannelEdit{PermissionOverwrites: newPermissions})
	}

	config.MuteRole = r.ID

	db.SetGuildConfig(guildID, config)

	return r.ID, nil
}

// NumberMapping is a mapping of 0-10 to emojis of the same values
var NumberMapping = map[int]string{
	0:  "0️⃣",
	1:  "1️⃣",
	2:  "2️⃣",
	3:  "3️⃣",
	4:  "4️⃣",
	5:  "5️⃣",
	6:  "6️⃣",
	7:  "7️⃣",
	8:  "8️⃣",
	9:  "9️⃣",
	10: "🔟",
}

// GetNow returns the current time in the format discord uses for timestamps
func GetNow() string {
	return time.Now().Format(time.RFC3339)
}

// var discordPermMap = map[int]string{
// 	0x00000001: "CREATE_INSTANT_INVITE",
// 	0x00000002: "KICK_MEMBERS",
// 	0x00000004: "BAN_MEMBERS",
// 	0x00000008: "ADMINISTRATOR",
// 	0x00000010: "MANAGE_CHANNELS",
// 	0x00000020: "MANAGE_GUILD",
// 	0x00000040: "ADD_REACTIONS",
// 	0x00000080: "VIEW_AUDIT_LOG",
// 	0x00000100: "PRIORITY_SPEAKER",
// 	0x00000200: "STREAM",
// 	0x00000400: "VIEW_CHANNEL",
// 	0x00000800: "SEND_MESSAGES",
// 	0x00001000: "SEND_TTS_MESSAGES",
// 	0x00002000: "MANAGE_MESSAGES",
// 	0x00004000: "EMBED_LINKS",
// 	0x00008000: "ATTACH_FILES",
// 	0x00010000: "READ_MESSAGE_HISTORY",
// 	0x00020000: "MENTION_EVERYONE",
// 	0x00040000: "USE_EXTERNAL_EMOJIS",
// 	0x00080000: "VIEW_GUILD_INSIGHTS",
// 	0x00100000: "CONNECT",
// 	0x00200000: "SPEAK",
// 	0x00400000: "MUTE_MEMBERS",
// 	0x00800000: "DEAFEN_MEMBERS",
// 	0x01000000: "MOVE_MEMBERS",
// 	0x02000000: "USE_VAD",
// 	0x04000000: "CHANGE_NICKNAME",
// 	0x08000000: "MANAGE_NICKNAMES",
// 	0x10000000: "MANAGE_ROLES",
// 	0x20000000: "MANAGE_WEBHOOKS",
// 	0x40000000: "MANAGE_EMOJIS",
// }
