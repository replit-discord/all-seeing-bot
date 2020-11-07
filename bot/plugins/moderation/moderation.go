package moderation

import (
	"fmt"
	"log"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/checks"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins/background"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins/logger"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"github.com/repl-it-discord/all-seeing-bot/util"
	"github.com/repl-it-discord/all-seeing-bot/util/perms"
)

type modPlugin struct {
	*types.BasePlugin
}

var loggerConfig = &logger.Config{
	Name:  "Moderation",
	Color: 0xff0000,
}

var zeroTime = time.Time{}

var plugin = &types.Plugin{
	Load: load,
	Commands: []interface{}{
		&types.CleanArgCommand{
			Name:    "mute",
			Aliases: []string{"silence"},

			Checks: []types.CheckFunc{
				checks.IsGuild,
				checks.HasPermissions(&bot, "mute", perms.Administrator, perms.ManageRoles, perms.BanMembers),
			},

			Exec: mute,
		},
		&types.CleanArgCommand{
			Name:    "unmute",
			Aliases: []string{"unsilence"},
			Checks: []types.CheckFunc{
				checks.IsGuild,
				checks.HasPermissions(&bot, "unmute", perms.Administrator, perms.ManageRoles, perms.BanMembers),
			},

			Exec: unmute,
		},
	},
}

var bot *discordgo.Session

func load(s *discordgo.Session) error {
	bot = s

	background.RegisterTask("mutes", background.Task{
		Interval: time.Second,
		Run: func() {
			mutes, err := db.GetMutes()

			if err != nil {
				// Panics will be handled
				panic(err)
			}

			for _, m := range mutes {
				if !m.ExpiresAt.Equal(zeroTime) && time.Now().After(m.ExpiresAt) {
					go clearRecord(m)
				}
			}
		},
	})

	bot.AddHandler(handleJoin)

	return nil
}

func handleJoin(s *discordgo.Session, m *discordgo.GuildMemberAdd) {
	fmt.Println("wtf")

	mute := &db.GuildMute{
		UserID:  m.User.ID,
		GuildID: m.GuildID,
	}

	err := db.GetMute(mute)

	// User is fine, they're not muted
	if err != nil {
		fmt.Println("oof", err)
		return
	}

	mr, err := util.GetMutedRole(s, m.GuildID, nil)

	if err != nil {
		return
	}

	s.GuildMemberRoleAdd(m.GuildID, m.User.ID, mr)

}

func init() {
	plugins.Register(plugin)
}

func mute(
	m *discordgo.Message,
	args []string,
) {

	if len(args) == 0 {
		bot.ChannelMessageSend(m.ChannelID, "error - no arguments provided.")

		return
	}

	member, err := util.ParseMember(bot, m.GuildID, args[0])

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "User not found")
		return
	}

	var expiration time.Time
	reason := ""

	if len(args) > 1 {
		duration, err := time.ParseDuration(args[1])

		// The argument isn't a duration, thats fine just add it to the reason
		if err != nil {
			reason = util.RepairArgs(args[1:])
		} else {
			if len(args) > 2 {
				reason = util.RepairArgs(args[2:])
			}

			expiration = time.Now().Add(duration)
		}
	}

	roleID, err := util.GetMutedRole(bot, m.GuildID, nil)

	err = bot.GuildMemberRoleAdd(m.GuildID, member.User.ID, roleID)

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "Could not fetch muted role. This should not happen, please contact the bot developer.")
		log.Println("unable to get return from util.GetMutedRole:", err)
		return
	}

	_, err = db.CreateGuildMuteRecord(&db.GuildMute{
		GuildID:   m.GuildID,
		UserID:    member.User.ID,
		ExpiresAt: expiration,
	})

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "Unable to create mute record, this should not happen - please contact the bot developer.")
		return
	}

	var message string = fmt.Sprintf("<@%s> muted <@%s>", m.Author.ID, member.User.ID)

	if !expiration.Equal(time.Time{}) {
		message += fmt.Sprintf(" for %s.", args[1])
	}

	fields := []*discordgo.MessageEmbedField{}

	if reason != "" {
		fields = append(fields, &discordgo.MessageEmbedField{
			Name:  "Reason",
			Value: reason,
		})
	}

	defer logger.Log(m.GuildID, logger.LogCreate{
		Author: &discordgo.MessageEmbedAuthor{
			Name:    fmt.Sprintf("%s#%s", m.Author.Username, m.Author.Discriminator),
			IconURL: m.Author.AvatarURL("128x128"),
		},
		Config:  loggerConfig,
		Message: message,
		Fields:  fields,
	})

	bot.ChannelMessageSend(m.ChannelID, "User muted")
}

func unmute(
	m *discordgo.Message,
	args []string,
) {
	if len(args) == 0 {
		bot.ChannelMessageSend(m.ChannelID, "error - no arguments provided.")

		return
	}

	member, err := util.ParseMember(bot, m.GuildID, args[0])

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "User not found")
		return
	}

	reason := ""

	if len(args) > 1 {
		reason = util.RepairArgs(args[1:])
	}

	mr, err := util.GetMutedRole(bot, m.GuildID, nil)

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "Could not fetch muted role. This should not happen, please contact the bot developer.")
		log.Println("unable to get return from util.GetMutedRole:", err)
		return
	}

	err = bot.GuildMemberRoleRemove(m.GuildID, member.User.ID, mr)

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "Error while removing user's muted role. This could mean that the bot does not have permission to do this.")
		return
	}

	fields := []*discordgo.MessageEmbedField{}

	if reason != "" {
		fields = append(fields, &discordgo.MessageEmbedField{
			Name:  "Reason",
			Value: reason,
		})
	}

	db.DeleteMute(&db.GuildMute{
		UserID:  member.User.ID,
		GuildID: m.GuildID,
	})

	defer logger.Log(m.GuildID, logger.LogCreate{
		Author: &discordgo.MessageEmbedAuthor{
			Name:    fmt.Sprintf("%s#%s", m.Author.Username, m.Author.Discriminator),
			IconURL: m.Author.AvatarURL("128x128"),
		},
		Config:  loggerConfig,
		Message: fmt.Sprintf("<@%s> unmuted <@%s>", m.Author.ID, member.User.ID),
		Fields:  fields,
	})

}

func clearRecord(m *db.GuildMute) {
	muterole, err := util.GetMutedRole(bot, m.GuildID, nil)

	if err != nil {
		log.Println("could not get config:", err)
		return
	}

	err = bot.GuildMemberRoleRemove(m.GuildID, m.UserID, muterole)

	if err, ok := err.(discordgo.RESTError); ok {
		if err.Response.StatusCode == 403 || err.Response.StatusCode == 404 {
			db.DeleteMute(m)
		}
		return
	}
	if err != nil {
		log.Println("could not unmute user:", err)
		return
	}

	err = db.DeleteMute(m)

	if err != nil {
		log.Println("wtf happened here:", err)
	}

	logger.Log(m.GuildID, logger.LogCreate{
		Config:  loggerConfig,
		Message: fmt.Sprintf("<@%s> has been automatically unmuted.", m.UserID),
	})
}
