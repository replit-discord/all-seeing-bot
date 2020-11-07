package handlers

import (
	"log"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
)

var plugin = &types.Plugin{
	Load: load,
}

func load(s *discordgo.Session) error {
	// This plugin is only for loading CORE handlers - everything else
	// should belong to its own plugin
	s.AddHandler(handleJoin)
	s.AddHandler(handleLeave)

	for _, g := range s.State.Guilds {
		err := s.RequestGuildMembers(g.ID, "", 0, false)

		if err != nil {
			return err
		}
	}

	return nil
}

func init() {
	plugins.Register(plugin)
}

func handleChunk(s *discordgo.Session, m *discordgo.GuildMembersChunk) {
	guild, err := s.State.Guild(m.GuildID)

	if err != nil {
		log.Print("Unable to set members for "+m.GuildID+":", err)
	}

	guild.Members = m.Members
}

func handleJoin(s *discordgo.Session, m *discordgo.GuildMemberAdd) {
	guild, err := s.State.Guild(m.GuildID)

	if err != nil {
		return
	}

	guild.Members = append(guild.Members, m.Member)
}

func handleLeave(s *discordgo.Session, m *discordgo.GuildMemberRemove) {
	guild, err := s.State.Guild(m.GuildID)

	if err != nil {
		return
	}

	index := 0

	for i, v := range guild.Members {
		if v.User.ID == m.User.ID {
			index = i
		}
	}

	guild.Members[index] = guild.Members[len(guild.Members)-1]
	guild.Members = guild.Members[:len(guild.Members)-1]
}
