package help

import "github.com/repl-it-discord/all-seeing-bot/bot/types"

// PluginInfo is the info used for the plugin's description in the help command.
type PluginInfo struct {
	*types.Plugin `yaml:"-"`
	Description   string                  `yaml:"description"`
	Emoji         string                  `yaml:"emoji"`
	Commands      map[string]*commandInfo `yaml:"commands"`
	Color         int                     `yaml:"color"`
}

type commandParamater struct {
	Name        string `yaml:"name"`
	Optional    bool   `yaml:"optional"`
	Description string `yaml:"description"`
}

// commandInfo is the info for a plugin
type commandInfo struct {
	*types.Command `yaml:"-"`
	plugin         *PluginInfo
	Paramaters     []commandParamater `yaml:"params"`
	Description    string             `yaml:"description"`
	// Short is a short version of description
	Short string `yaml:"short"`
	Color int    `yaml:"color"`
}
