package help

import (
	"fmt"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"github.com/repl-it-discord/all-seeing-bot/util"
)

func createMainHelp(m *discordgo.Message) (*discordgo.MessageEmbed, []string) {
	fields := []*discordgo.MessageEmbedField{}
	reactions := []string{}

	for _, n := range pluginNames {
		p, _ := pluginInfo[n]

		if p.Check == nil {
			fields = append(fields, &discordgo.MessageEmbedField{
				Name:  util.Bold(fmt.Sprintf("%s %s", p.Emoji, util.CapitalizeFirst(n))),
				Value: p.Description,
			})
			reactions = append(reactions, p.Emoji)
			continue
		}

		if p.Check(m) {
			fields = append(fields, &discordgo.MessageEmbedField{
				Name:  util.Bold(fmt.Sprintf("%s %s", p.Emoji, util.CapitalizeFirst(n))),
				Value: p.Description,
			})
			reactions = append(reactions, p.Emoji)
		}
	}

	return &discordgo.MessageEmbed{
		Title:     util.Bold("Help"),
		Author:    util.GetAuthor(m.Author),
		Fields:    fields,
		Timestamp: util.GetNow(),
	}, reactions
}

func helpErrEmbed(m *discordgo.Message) *discordgo.MessageEmbed {
	return &discordgo.MessageEmbed{
		Title:       "Error",
		Author:      util.GetAuthor(m.Author),
		Color:       0xff0000,
		Description: "Unknown command or plugin",
		Timestamp:   util.GetNow(),
	}
}

func createPluginHelp(m *discordgo.Message, name string) (*discordgo.MessageEmbed, []string) {
	reactions := []string{backEmoji}

	p, ok := pluginInfo[name]

	if !ok {
		return helpErrEmbed(m), reactions
	}

	allowedCommands := map[string]*commandInfo{}

	for _, n := range commandNames {
		c, ok := p.Commands[n]
		if !ok {
			continue
		}

		canUse := true
		for _, check := range c.Checks {
			if canUse = check(m); !canUse {
				break
			}
		}

		if canUse {
			allowedCommands[n] = c
		}
	}

	if len(allowedCommands) == 0 {
		return &discordgo.MessageEmbed{
			Title:       util.Bold(util.CapitalizeFirst(name)),
			Author:      util.GetAuthor(m.Author),
			Color:       p.Color,
			Description: "You do not have permission to use any commands in this plugin here.",
		}, reactions
	}

	reactions = append(reactions, nextEmoji)

	embedDesc := ""

	for n, c := range allowedCommands {
		var cmdHelp string
		if c.Short != "" {
			cmdHelp = c.Short
		} else {
			cmdHelp = c.Description
		}

		embedDesc += util.Bold(n) + ": " + cmdHelp + "\n"
	}

	return &discordgo.MessageEmbed{
		Title:       util.Bold(util.CapitalizeFirst(name)),
		Author:      util.GetAuthor(m.Author),
		Description: embedDesc,
		Color:       p.Color,
		Timestamp:   util.GetNow(),
	}, reactions
}

func createCommandHelp(m *discordgo.Message, session *db.HelpSession) (*discordgo.MessageEmbed, []string) {
	reactions := []string{backEmoji}

	// This shouldn't happen, but if so there's no reason why we shouldn't return the correct embed
	if session.Page == -1 {
		return createPluginHelp(m, session.Plugin)
	}

	p, ok := pluginInfo[session.Plugin]

	if !ok {
		return helpErrEmbed(m), reactions
	}

	var cmd *commandInfo
	index := 0

	allowedCommands := map[string]*commandInfo{}

	for _, n := range commandNames {
		c, ok := p.Commands[n]
		if !ok {
			continue
		}

		canUse := true
		for _, check := range c.Checks {
			if canUse = check(m); !canUse {
				break
			}
		}

		if canUse {
			allowedCommands[n] = c
			if session.Page == index {
				cmd = c
			}
			index++
		}
	}

	if cmd == nil {
		return helpErrEmbed(m), reactions
	}

	color := cmd.Color

	if color == 0 {
		color = p.Color
	}

	reactions = append(reactions, previousEmoji)

	if session.Page != len(allowedCommands)-1 {
		reactions = append(reactions, nextEmoji)
	}

	prefix := "?"

	if m.GuildID != "" {
		if config, err := db.GetGuildConfig(m.GuildID); err == nil {
			prefix = config.Prefix
		}
	}

	desc := prefix + cmd.Name
	argDesc := ""

	for _, arg := range cmd.Paramaters {
		desc += " "

		if arg.Optional {
			desc += "[" + arg.Name + "]"
			argDesc += util.Bold(arg.Name) + " *(optional)*: " + arg.Description + "\n"
			continue
		}

		desc += arg.Name
		argDesc += util.Bold(arg.Name) + ": " + arg.Description + "\n"

	}

	fields := []*discordgo.MessageEmbedField{
		{
			Name:  "Description",
			Value: cmd.Description,
		},
	}

	if len(cmd.Aliases) > 0 {
		fields = append(fields, &discordgo.MessageEmbedField{
			Name:  "Aliases",
			Value: strings.Join(cmd.Aliases, ", "),
		})
	}

	if argDesc != "" {
		fields = append(fields, &discordgo.MessageEmbedField{
			Name:  "Arguments",
			Value: argDesc,
		})
	}

	return &discordgo.MessageEmbed{
		Title:       util.Bold(util.CapitalizeFirst(cmd.Name)),
		Description: desc,
		Color:       color,
		Fields:      fields,
		Timestamp:   util.GetNow(),
		Author:      util.GetAuthor(m.Author),
		Footer: &discordgo.MessageEmbedFooter{
			Text: fmt.Sprintf("Command %d/%d", session.Page+1, len(allowedCommands)),
		},
	}, reactions

}
