package logger

import (
	"fmt"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/db"
)

// Log sends a log to a guild's log channel
func Log(guildID string, l LogCreate) {
	config, err := db.GetGuildConfig(guildID)
	fmt.Println("hi")
	if err != nil {
		fmt.Println("config != nil")
		return
	}

	if config.LogChannel == "" {
		fmt.Println("logchannel is zero")
		return
	}

	m, e := bot.ChannelMessageSendEmbed(config.LogChannel, &discordgo.MessageEmbed{
		Title:       l.Config.Name,
		Author:      l.Author,
		Color:       l.Config.Color,
		Description: l.Message,
		Fields:      l.Fields,
		Timestamp:   time.Now().Format(time.RFC3339),
	})

	fmt.Println(m, e)
}
