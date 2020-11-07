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
	Checks  []CheckFunc
	Exec    CleanArgCommandFunc
	Plugin  *Plugin
}

// Command is a basic command
type Command struct {
	Name    string
	Aliases []string
	Checks  []CheckFunc
	Exec    RawArgCommandFunc
	Plugin  *Plugin
}

// Plugin is an interface used by the bot to register a plugin
type Plugin struct {
	Load     func(s *discordgo.Session) error
	Check    func(m *discordgo.Message) bool
	Commands []interface{}
	Close    func()
}

// BasePlugin is a basic plugin that plugins probably want to embed
type BasePlugin struct {
	S *discordgo.Session
}

// Load is used to set the plugins config and session
func (p *BasePlugin) Load(s *discordgo.Session) {
	p.S = s
}

// Closeable is an interface for objects which have a Close() method
type Closeable interface {
	Close()
}
