package plugins

import (
	"fmt"
	"reflect"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/util"
)

var intents discordgo.Intent
var plugins = []*types.Plugin{}

// Register is used to register plugins for the bot
func Register(p *types.Plugin) {
	plugins = append(plugins, p)
	intents |= p.Intents
}

var commands = []*types.Command{}

func chkNotNil(v interface{}, info ...string) {
	if reflect.ValueOf(v).IsNil() {
		panic(fmt.Errorf("%s nil", strings.Join(info, " ")))
	}
}

// LoadPlugins iterates through the known plugins and loads them
func LoadPlugins(s *discordgo.Session) error {
	for _, plugin := range plugins {
		if plugin.Load != nil {
			err := plugin.Load(s)
			if err != nil {
				return err
			}
		}

		for _, cmd := range plugin.Commands {
			switch c := cmd.(type) {
			case *types.CleanArgCommand:
				chkNotNil(c.Exec, c.Name, "exec")
				c.Plugin = plugin
				commands = append(
					commands,
					&types.Command{
						Name:    c.Name,
						Aliases: c.Aliases,
						Checks:  c.Checks,
						Plugin:  c.Plugin,
						Exec: func(
							m *discordgo.Message,
							args string,
						) {
							c.Exec(m, util.ParseArgs(args))
						},
					},
				)
				break
			case *types.Command:
				chkNotNil(c.Exec, c.Name, "exec")
				c.Plugin = plugin
				commands = append(commands, c)
				break
			default:
				panic(fmt.Errorf("Unknown command type: %s", reflect.TypeOf(c).Name()))

			}
		}
	}

	for _, plugin := range plugins {
		if plugin.AfterLoad != nil {
			plugin.AfterLoad()
		}
	}

	return nil
}

// GetIntents is used to get the intents that the plugins need
func GetIntents() discordgo.Intent {
	return intents
}

// Close is used to close all plugins which need to be closed before the bot shut downs
func Close() {
	for _, p := range plugins {
		if p.Close != nil {
			p.Close()
		}
	}
}

// GetCommands is used to get the commands from the loaded plugins
func GetCommands() []*types.Command {
	return commands
}
