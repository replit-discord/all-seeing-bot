package logger

import (
	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"github.com/repl-it-discord/all-seeing-bot/util"
)

// Log sends a log to a guild's log channel
func Log(guildID string, l LogCreate) {
	config, err := db.GetGuildConfig(guildID)

	if err != nil {
		return
	}

	if config.LogChannel == "" {
		return
	}

	bot.ChannelMessageSendEmbed(config.LogChannel, &discordgo.MessageEmbed{
		Title:       l.Config.Name,
		Author:      l.Author,
		Color:       l.Config.Color,
		Description: l.Message,
		Fields:      l.Fields,
		Timestamp:   util.GetNow(),
	})
}
