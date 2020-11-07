package config

import (
	"fmt"
	"log"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/checks"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins/logger"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"github.com/repl-it-discord/all-seeing-bot/util"
	"github.com/repl-it-discord/all-seeing-bot/util/perms"
)

type configPlugin struct {
}

// Check is the global check applied to all commands in the plugin.
func (p *configPlugin) Check(m *discordgo.Message) bool {
	return checks.IsGuild(m)
}

var plugin = &types.Plugin{
	Commands: []interface{}{
		&types.Command{
			Name: "prefix",

			Exec: prefix,
			Checks: []types.CheckFunc{
				checks.HasPermissions(&bot, "prefix", perms.Administrator, perms.ManageGuild),
			},
		},
		&types.Command{
			Name:    "setloggerchannel",
			Aliases: []string{"slc", "lc", "logchannel", "loggerchannel"},
			Checks: []types.CheckFunc{
				checks.HasPermissions(&bot, "setloggerchannel", perms.Administrator, perms.ManageGuild),
			},

			Exec: setLogChannel,
		},
	},
}

var loggerConfig = &logger.Config{
	Name:  "Config",
	Color: 0xffffff,
}

var bot *discordgo.Session

func load(s *discordgo.Session) error {
	bot = s

	return nil
}

func init() {
	plugins.Register(plugin)
}

func prefix(m *discordgo.Message, args string) {
	config, err := db.GetGuildConfig(m.GuildID)

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "Unable to get server config. This should not happen, please contact the bot developer.")
		log.Println("error fetching config:", err)
		return
	}

	config.Prefix = args

	err = db.SetGuildConfig(m.GuildID, config)

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "Unable to set server config. This should not happen, please contact the bot developer.")
		log.Println("error setting config:", err)
		return
	}

	defer logger.Log(m.GuildID, logger.LogCreate{
		Config:  loggerConfig,
		Message: fmt.Sprintf("<@%s> set the server prefix to %s", m.Author.ID, args),
		Author:  util.GetAuthor(m.Author),
	})

	bot.ChannelMessageSend(m.ChannelID, "Set the server prefix to "+args)
}

func setLogChannel(m *discordgo.Message, c string) {
	config, err := db.GetGuildConfig(m.GuildID)

	if err != nil {
		bot.ChannelMessageSend(
			m.ChannelID,
			"Could not find a config for this user. This should not happen, please contact the bot developer.",
		)
		return
	}

	channel, err := util.ParseChannel(bot, m.GuildID, c)

	if err != nil {
		return
	}

	config.LogChannel = channel.ID

	err = db.SetGuildConfig(m.GuildID, config)

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "An error occurred while updating the servers config. This should not happen, please contact the bot developer.")
		return
	}

	bot.ChannelMessageSend(m.ChannelID, "Guild configuration updated successfully")
}
