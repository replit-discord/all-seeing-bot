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
	Name    string
	Aliases []string
	Plugin  Plugin
	Checks  []CheckFunc
	Exec    CleanArgCommandFunc
}

// Command is a basic command
type Command struct {
	Name    string
	Aliases []string
	Plugin  Plugin
	Checks  []CheckFunc
	Exec    RawArgCommandFunc
}

// Plugin is an interface used by the bot to register a plugin
type Plugin interface {
	Load(s *discordgo.Session) ([]interface{}, error)
}

// PluginWithChecks is a normal plugin with global checks
type PluginWithChecks interface {
	Plugin
	Check(m *discordgo.Message) bool
}

// BasePlugin is a basic plugin that plugins probably want to embed
type BasePlugin struct {
	S *discordgo.Session
}

// Load is used to set the plugins config and session
func (p *BasePlugin) Load(s *discordgo.Session) {
	p.S = s
}
