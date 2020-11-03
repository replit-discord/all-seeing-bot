package dev

import (
	"regexp"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/util"
)

type devPlugin struct {
	*types.BasePlugin
}

// Check is the global check applied to all commands in the plugin.
func (p *devPlugin) Check(m *discordgo.Message) bool {
	for _, d := range util.DevIDs {
		if d == m.Author.ID {
			return true
		}
	}

	return false
}

var queryCommandRegex *regexp.Regexp

var plugin = &devPlugin{BasePlugin: &types.BasePlugin{}}

var commands = []interface{}{
	&types.Command{
		Name:   "echo",
		Plugin: plugin,

		Exec: echo,
	},
}

func check(m discordgo.Message) bool {
	return true
}

var bot *discordgo.Session

// Load is used to get plugins and load the plugin
func (p *devPlugin) Load(s *discordgo.Session) ([]interface{}, error) {
	p.BasePlugin.Load(s)
	bot = s

	return commands, nil
}

func init() {
	plugins.Register(plugin)
}

func echo(
	m *discordgo.Message,
	args string,
) {
	// TODO: Also work in dms
	msg := args
	channelID := m.ChannelID

	if splitArgs := strings.SplitN(args, " ", 2); len(splitArgs) > 1 {
		if util.ChannelMentionRegex.MatchString(splitArgs[0]) {
			channelID = util.NumberRegex.FindString(splitArgs[0])
			msg = splitArgs[1]
		} else if util.UserMentionRegex.MatchString(splitArgs[0]) {
			channel, err := bot.UserChannelCreate(util.NumberRegex.FindString(splitArgs[0]))
			if err == nil {
				channelID = channel.ID
				msg = splitArgs[1]
			}
		}
	}

	if _, err := bot.ChannelMessageSend(channelID, msg); err != nil {
		bot.ChannelMessageSend(m.ChannelID, msg)
	}
}
