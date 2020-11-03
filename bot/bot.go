package bot

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
	// "github.com/repl-it-discord/all-seeing-bot/bot/commands"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/db"

	// Plugin registering
	_ "github.com/repl-it-discord/all-seeing-bot/bot/plugins/dev"
)

var bot *discordgo.Session
var commands []*types.Command

func chk(err error) {
	if err != nil {
		panic(err)
	}
}

const (
	host = "postgres"
	port = 5432
	user = "allawesome497"

	dbname = "allseeingbot"
)

// Run runs the bot
func Run() {
	var err error
	bot, err = discordgo.New("Bot " + os.Getenv("BOT_TOKEN"))
	bot.StateEnabled = true
	chk(err)

	// register events
	bot.AddHandler(ready)

	chk(bot.Open())

	chk(err)

	chk(plugins.LoadPlugins(bot))

	commands = plugins.GetCommands()

	bot.AddHandler(handleMessage)
}

// Kill will stop the bot and close connections
func Kill() {
	err := bot.Close()
	if err != nil {
		panic(err)
	}
}

func ready(s *discordgo.Session, event *discordgo.Ready) {
	s.UpdateStatus(0, "everything")
	fmt.Printf("Logged in as %s#%s\n", s.State.User.Username, s.State.User.Discriminator)

}

func handleMessage(s *discordgo.Session, m *discordgo.MessageCreate) {

	if m.Author.Bot {
		return
	}

	// r, t := util.ParseMention(bot, "585606083897458691", m.Content)

	// fmt.Println(r, t)

	config, err := db.GetGuildConfig(m.GuildID)

	if err != nil {
		panic(err)
	}

	if strings.HasPrefix(m.Content, string(config.Prefix)) {
		go handleCommand(s, m, config)
	}
}

func handleCommand(s *discordgo.Session, m *discordgo.MessageCreate, config *db.GuildConfigType) {

	cleanString := strings.TrimPrefix(m.Content, config.Prefix)

	splitString := strings.SplitN(cleanString, " ", 2)
	command := strings.ToLower(splitString[0])
	args := ""

	if len(splitString) == 2 {
		args = splitString[1]
	}

	var cmd *types.Command = nil

	for _, c := range commands {
		if cmd != nil {
			break
		}

		if c.Name == command {
			cmd = c
			break
		}

		for _, a := range c.Aliases {
			if a == command {
				cmd = c
				break
			}
		}

	}

	if cmd == nil {
		channel, err := s.UserChannelCreate(m.Author.ID)

		if err != nil {
			return
		}

		_, err = s.ChannelMessageSend(channel.ID, "Invalid command")

		return
	}

	noPerms := func() {
		msg, err := s.ChannelMessageSend(m.ChannelID, "You do not have permission to do this here.")

		if err != nil {
			return
		}

		time.Sleep(time.Second * 3)

		s.ChannelMessageDelete(msg.ChannelID, msg.ID)
	}

	plugin := cmd.Plugin

	if pluginWithChecks, ok := plugin.(types.PluginWithChecks); ok {
		if !pluginWithChecks.Check(m.Message) {
			noPerms()
			return
		}
	}

	for _, check := range cmd.Checks {
		if !check(m.Message) {
			noPerms()
			return
		}
	}

	cmd.Exec(m.Message, args)
}
