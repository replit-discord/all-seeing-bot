package dev

import (
	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/util"
)

var plugin = &types.Plugin{
	Load:     load,
	Check:    check,
	Commands: commands,
}

func check(m *discordgo.Message) bool {
	for _, d := range util.DevIDs {
		if d == m.Author.ID {
			return true
		}
	}

	return false
}

var commands = []interface{}{
	&types.CleanArgCommand{
		Name: "echo",

		Exec: echo,
	},
}

var bot *discordgo.Session

func load(s *discordgo.Session) error {
	bot = s

	return nil
}

func init() {
	plugins.Register(plugin)
}

func echo(
	m *discordgo.Message,
	args []string,
) {
	msg := util.RepairArgs(args)
	channelID := m.ChannelID

	if len(args) > 1 {

		if c, err := util.ParseChannel(bot, m.GuildID, args[0]); err == nil {
			channelID = c.ID
			msg = util.RepairArgs(args[1:])
		} else if m, err := util.ParseMember(bot, m.GuildID, args[0]); err == nil {
			channel, err := bot.UserChannelCreate(m.User.ID)
			if err == nil {
				channelID = channel.ID
				msg = util.RepairArgs(args[1:])
			}
		}
	}

	if _, err := bot.ChannelMessageSend(channelID, msg); err != nil {
		bot.ChannelMessageSend(m.ChannelID, msg)
		bot.MessageReactionAdd(m.ChannelID, m.ID, "😢")
		return
	}

	bot.MessageReactionAdd(m.ChannelID, m.ID, "🙂")
}
