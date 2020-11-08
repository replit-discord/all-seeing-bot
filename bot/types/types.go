package types

import (
	"github.com/bwmarrin/discordgo"
)

// CleanArgCommandFunc is the function used to actually execute the command
type CleanArgCommandFunc func(
	m *discordgo.Message,
	args []string,
)

// RawArgCommandFunc is the function used to actually execute the command
type RawArgCommandFunc func(
	m *discordgo.Message,
	args string,
)

// CheckFunc is a function that is used to check whether a user can use the command or not.
type CheckFunc func(
	m *discordgo.Message,
) bool

// CleanArgCommand is a command that gets parsed args
type CleanArgCommand struct {
	// Name is the name of the command
	Name string
	// Aliases are aliases for the command
	Aliases []string
	// Checks are the checks used for the plugin, any permission checks should be listed here.
	Checks []CheckFunc
	// Exec is the function used to run the comand. The arguments are the message and the raw arguments.
	Exec CleanArgCommandFunc
	// Plugin is the plugin that the command belongs to. This is set when
	// we register the plugin, and should not be changed anywhere else.
	Plugin *Plugin
}

// Command is a basic command
type Command struct {
	// Name is the name of the command
	Name string
	// Aliases are aliases for the command
	Aliases []string
	// Checks are the checks used for the plugin, any permission checks should be listed here.
	Checks []CheckFunc
	// Exec is the function used to run the comand. The arguments are the message and the raw arguments.
	Exec RawArgCommandFunc
	// Plugin is the plugin that the command belongs to. This is set when
	// we register the plugin, and should not be changed anywhere else.
	Plugin *Plugin
}

// Plugin is an interface used by the bot to register a plugin
type Plugin struct {
	// Load is a function which is called when we load the plugin.
	Load func(s *discordgo.Session) error
	// AfterLoad is called after every plugin plugin has been loaded.
	AfterLoad func()
	// Check is a global check for all commands in the plugin
	Check func(m *discordgo.Message) bool
	// Commands is a list of commands for the bot.
	Commands []interface{}
	// Close is called when the bot is disconnecting, if anything needs to be disconnected
	// or can be closed otherwise it should be handled here.
	Close func()
	// Intents are the discord intents that the plugin might require. If you add a handler
	// of any type to the plugin the intent for that event should be here, regardless
	// of it being stated anywhere else.
	//
	// https://discord.com/developers/docs/topics/gateway#gateway-intents
	Intents discordgo.Intent
}
