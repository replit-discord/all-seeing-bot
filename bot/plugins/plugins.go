package plugins

import (
	"fmt"
	"reflect"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/util"
)

var plugins = []types.Plugin{}

// Register is used to register plugins for the bot
func Register(plugin types.Plugin) {
	plugins = append(plugins, plugin)
}

var commands = []*types.Command{}

// LoadPlugins iterates through the known plugins and loads them
func LoadPlugins(s *discordgo.Session) error {
	for _, plugin := range plugins {
		cmds, err := plugin.Load(s)
		if err != nil {
			return err
		}

		for _, cmd := range cmds {
			switch c := cmd.(type) {
			case *types.CleanArgCommand:
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
				commands = append(commands, c)
				break
			default:
				panic(fmt.Errorf("Unknown command type: %s", reflect.TypeOf(c).Name()))

			}
		}

	}

	return nil
}

// GetCommands is used to get the commands from the loaded plugins
func GetCommands() []*types.Command {
	return commands
}
