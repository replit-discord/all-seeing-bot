package help

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/checks"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"gopkg.in/yaml.v3"
)

const (
	backEmoji     = "↩️"
	previousEmoji = "◀️"
	nextEmoji     = "▶️"
)

var bot *discordgo.Session

var plugin = &types.Plugin{
	Load:      load,
	AfterLoad: afterLoad,
	Intents:   discordgo.IntentsDirectMessageReactions | discordgo.IntentsGuildMessageReactions,
	Commands: []interface{}{
		&types.Command{
			Name: "help",
			Checks: []types.CheckFunc{
				checks.HasPermission(&bot, "help", true),
			},
			Exec: help,
		},
	},
}

var (
	pluginInfo   = map[string]*PluginInfo{}
	pluginNames  = []string{}
	commandNames = []string{}
)

func init() {
	f, err := os.Open("bot/plugins.yaml")

	if err != nil {
		log.Panic("Unable to fetch plugin help:", err)
	}
	dat, err := ioutil.ReadAll(f)

	if err != nil {
		log.Panic("Unable to read plugin help:", err)
	}

	err = yaml.Unmarshal(dat, &pluginInfo)

	if err != nil {
		panic(err)
	}

	for n := range pluginInfo {
		pluginNames = append(pluginNames, n)
	}

	Register("help", plugin)
	plugins.Register(plugin)
}

func afterLoad() {
	commands := plugins.GetCommands()
	for _, c := range commands {
		commandNames = append(commandNames, c.Name)
		for _, p := range pluginInfo {
			if cmdInfo, ok := p.Commands[c.Name]; ok {
				cmdInfo.Command = c
				break
			}
		}
	}
}

func load(s *discordgo.Session) error {
	bot = s

	for n, p := range pluginInfo {
		if p.Plugin == nil {
			panic(fmt.Errorf("help: unable to find plugin for %s", n))
		}
	}

	s.AddHandler(handleReaction)

	return nil
}

func handleReaction(s *discordgo.Session, r *discordgo.MessageReactionAdd) {
	if r.UserID == s.State.User.ID {
		return
	}

	session, err := db.GetHelpSession(r.UserID)

	if err != nil || session.MessageID != r.MessageID {
		log.Println(err)
		return
	}

	m, err := bot.ChannelMessage(r.ChannelID, session.MessageID)

	if r.GuildID != "" {
		member, err := bot.GuildMember(r.GuildID, r.UserID)
		if err != nil {
			return
		}

		m.Member = member
		m.Author = member.User
	} else {
		user, err := bot.User(r.UserID)
		if err != nil {
			return
		}
		m.Author = user
	}

	if err != nil {
		return
	}

	if r.Emoji.Name == backEmoji {
		embed, reactions := createMainHelp(m)
		session.Plugin = ""
		session.Page = -1
		db.SetHelpSession(r.UserID, session)
		updateHelp(m, embed, reactions)
		return
	}

	for n, p := range pluginInfo {
		if p.Emoji == r.Emoji.Name {
			session.Plugin = n
			session.Page = -1
			db.SetHelpSession(r.UserID, session)
			embed, reactions := createPluginHelp(m, n)

			updateHelp(m, embed, reactions)
			return
		}
	}

	if session.Plugin == "" ||
		(r.Emoji.Name != nextEmoji && r.Emoji.Name != previousEmoji) {
		return
	}

	if r.Emoji.Name == previousEmoji && session.Page == 0 {
		session.Page = -1

		_, ok := pluginInfo[session.Plugin]
		if !ok {
			embed, reactions := createMainHelp(m)
			session.Plugin = ""
			session.Page = -1
			db.SetHelpSession(r.UserID, session)
			updateHelp(m, embed, reactions)
			return
		}

		session.Page = -1
		db.SetHelpSession(r.UserID, session)
		embed, reactions := createPluginHelp(m, session.Plugin)

		updateHelp(m, embed, reactions)
		return
	}

	p, ok := pluginInfo[session.Plugin]

	if !ok {
		embed, reactions := createMainHelp(m)
		session.Plugin = ""
		session.Page = -1
		db.SetHelpSession(r.UserID, session)
		updateHelp(m, embed, reactions)
		return
	}

	count := 0

	for _, c := range p.Commands {
		canUse := true
		for _, check := range c.Checks {
			if canUse = check(m); !canUse {
				break
			}
		}

		if canUse {
			count++
		}
	}

	if r.Emoji.Name == nextEmoji {
		if session.Page == count-1 {
			return
		}

		session.Page++
		db.SetHelpSession(r.UserID, session)
		embed, reactions := createCommandHelp(m, session)
		updateHelp(m, embed, reactions)
		return
	}

	session.Page--

	db.SetHelpSession(r.UserID, session)

	embed, reactions := createCommandHelp(m, session)
	updateHelp(m, embed, reactions)

}

// Register is used to register a plugin for help
func Register(name string, p *types.Plugin) {
	info, ok := pluginInfo[name]

	if !ok {
		panic(fmt.Errorf("Plugin registered but not found in bot/plugins.yaml: %s", name))
	}

	info.Plugin = p
}

func help(m *discordgo.Message, args string) {

	if args == "" {

		embed, reactions := createMainHelp(m)
		sendHelp(m, embed, reactions)

	}
	args = strings.ToLower(args)

	if _, ok := pluginInfo[args]; ok {
		embed, reactions := createPluginHelp(m, args)
		sendHelp(m, embed, reactions)
	}
}

func updateHelp(m *discordgo.Message, embed *discordgo.MessageEmbed, reactions []string) {
	bot.MessageReactionsRemoveAll(m.ChannelID, m.ID)

	msg, err := bot.ChannelMessageEditEmbed(m.ChannelID, m.ID, embed)

	if err != nil {
		// *if the bot doesn't have perms this will also error so they won't see this either.
		bot.ChannelMessageSend(m.ChannelID, "Unable to send help. This should not happen, please contact the bot developer.")
		return
	}

	for _, r := range reactions {
		bot.MessageReactionAdd(msg.ChannelID, msg.ID, r)
	}
}

func sendHelp(m *discordgo.Message, embed *discordgo.MessageEmbed, reactions []string) {
	msg, err := bot.ChannelMessageSendEmbed(m.ChannelID, embed)
	if err != nil {
		// *if the bot doesn't have perms this will also error so they won't see this either.
		bot.ChannelMessageSend(m.ChannelID, "Unable to send help. This should not happen, please contact the bot developer.")
		return
	}

	err = db.CreateHelpSession(m.Author.ID, msg.ID)

	if err != nil {
		bot.ChannelMessageDelete(msg.ChannelID, m.ID)
		bot.ChannelMessageSend(msg.ChannelID, "Unable to create help session.")
		return
	}

	for _, r := range reactions {
		bot.MessageReactionAdd(msg.ChannelID, msg.ID, r)
	}
}
