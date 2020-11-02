package commands

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"github.com/repl-it-discord/all-seeing-bot/util"
)

type command = func(
	s *discordgo.Session,
	m *discordgo.MessageCreate,
	config *db.GuildConfigType,
	command string,
	args *string,
) *string

var commands = map[string]command{
	"echo":         echo,
	"updateconfig": updateConfig,
	"getconfig":    getConfig,
	"mute":         mute,
}

var isNumber func(string) bool

func init() {
	isNumber = regexp.MustCompile(`^\d+$`).MatchString
}

// RegisterEvents adds the handlers for commands to the bot
func RegisterEvents(b *discordgo.Session) {
	b.AddHandler(handleMessage)
}

func handleMessage(s *discordgo.Session, m *discordgo.MessageCreate) {

	if m.Author.Bot {
		return
	}

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
	var args *string

	if len(splitString) == 2 {
		args = &splitString[1]
	}

	exec, validCommand := commands[command]
	if !validCommand {
		channel, err := s.UserChannelCreate(m.Author.ID)

		if err != nil {
			return
		}

		_, err = s.ChannelMessageSend(channel.ID, "Invalid command")

		return
	}

	response := exec(s, m, config, command, args)

	if response != nil {
		s.ChannelMessageSend(m.ChannelID, *response)
	}
}

func echo(
	s *discordgo.Session,
	m *discordgo.MessageCreate,
	config *db.GuildConfigType,
	command string,
	args *string,
) *string {

	return args
}

func getConfig(
	s *discordgo.Session,
	m *discordgo.MessageCreate,
	config *db.GuildConfigType,
	command string,
	args *string,
) *string {
	var out string

	if !util.IsAdmin(s, m.Message) {
		out = "You do not have permission to do this"
		return &out
	}

	jsonBytes, err := json.MarshalIndent(config, "", "  ")

	if err != nil {
		out = "An unknown error occured"
		return &out
	}

	jsonRaw := string(jsonBytes)

	if len(jsonRaw) > 1900 {
		out = "Config too large"
		return &out
	}

	out = fmt.Sprintf("```json\n%s\n```", jsonRaw)
	return &out
}

func updateConfig(
	s *discordgo.Session,
	m *discordgo.MessageCreate,
	config *db.GuildConfigType,
	command string,
	args *string,
) *string {
	var out string

	if !util.IsAdmin(s, m.Message) {
		out = "You do not have permission to do this"
		return &out
	}

	if m.GuildID == "" {
		out = "This command can only be used in servers"
		return &out
	}

	cleanArgs := strings.SplitN(*args, " ", 2)

	if len(cleanArgs) == 1 {
		out = "Invalid arguments"
		return &out
	}

	configVar := strings.ToLower(cleanArgs[0])
	value := cleanArgs[1]
	out = "Config updated"

	switch configVar {
	case "prefix":
		config.Prefix = value

		err := db.SetGuildConfig(m.GuildID, config)
		if err != nil {
			out = "An unknown error occurred"
		}
		break
	case "muterole":
		roleID := strings.TrimPrefix(strings.TrimSuffix(value, ">"), "<@&")

		if !isNumber(roleID) {
			out = "Invalid value for muterole"
			break
		}

		_, err := s.State.Role(m.GuildID, roleID)

		if err != nil {
			out = "Role not found"
			break
		}

		config.MuteRole = roleID
		db.SetGuildConfig(m.GuildID, config)
		break
	default:
		out = fmt.Sprintf("Unknown config variable: %s", configVar)
		return &out
	}

	return &out
}
