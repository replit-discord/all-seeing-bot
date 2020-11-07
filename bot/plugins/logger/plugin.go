package logger

import (
	"regexp"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
)

var plugin = &types.Plugin{
	Load: load,
}

var pluginConfig = &Config{
	Color: 0xffffff,
	Name:  "Logs",
}

var queryCommandRegex *regexp.Regexp

func check(m discordgo.Message) bool {
	return true
}

var bot *discordgo.Session

func load(s *discordgo.Session) error {
	bot = s

	return nil
}

func init() {
	plugins.Register(plugin)
}
