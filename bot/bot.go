package bot

import (
	"fmt"
	"os"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/commands"
)

var bot *discordgo.Session

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
	commands.RegisterEvents(bot)

	err = bot.Open()

	if err != nil {
		panic(err)
	}

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
