package dev

import (
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
	"github.com/repl-it-discord/all-seeing-bot/db"
	"github.com/repl-it-discord/all-seeing-bot/util/perms"
)

var queryCommandRegex *regexp.Regexp

func load(s *discordgo.Session) error {
	bot = s
	s.AddHandler(handleMessage)

	return nil
}

var plugin = &types.Plugin{
	Load:    load,
	Intents: discordgo.IntentsDirectMessages | discordgo.IntentsGuildMessages,
	Commands: []interface{}{
		&types.Command{
			Name:    "setmodmailchannel",
			Aliases: []string{"mc", "smc", "modmailchannel"},
			Checks: []types.CheckFunc{
				func(m *discordgo.Message) bool {
					return m.GuildID != ""
				},
				func(m *discordgo.Message) bool {
					return perms.HasAnyPermissionsIn(bot, m, perms.Administrator)
				},
			},
			Exec: setModMailChannel,
		},
	},
}

var bot *discordgo.Session

func init() {
	plugins.Register(plugin)
}

func handleMessage(s *discordgo.Session, m *discordgo.MessageCreate) {
	if m.Author.Bot {
		return
	}
	channelID := m.ChannelID

	c, err := s.State.Channel(channelID)

	if err != nil {
		return
	}

	if c.Type == discordgo.ChannelTypeDM {
		userID := m.Message.Author.ID
		go handleDMMessage(s, m, userID)
		return
	}

	go handleGuildMessage(s, m, m.ChannelID)
}

func setModMailChannel(m *discordgo.Message, channel string) {
	config, err := db.GetGuildConfig(m.GuildID)

	if err != nil {
		bot.ChannelMessageSend(
			m.ChannelID,
			"Could not find a config for this user. This should not happen, please contact the bot developer.",
		)
		return
	}

	var categoryChannel *discordgo.Channel

	guild, err := bot.State.Guild(m.GuildID)

	// Should be nil unless the bot was removed from the server, in which case we won't be able to respond
	if err != nil {
		return
	}

	for _, c := range guild.Channels {
		if c.Type != discordgo.ChannelTypeGuildCategory {
			continue
		}

		if c.Name == channel || c.ID == channel {
			categoryChannel = c
		}

	}

	if categoryChannel == nil {
		bot.ChannelMessageSend(m.GuildID, "Category channel not found. Make sure you spelt it correctly.")
		return
	}

	config.ModmailCategoryID = categoryChannel.ID

	err = db.SetGuildConfig(m.GuildID, config)

	if err != nil {
		bot.ChannelMessageSend(m.ChannelID, "An error occurred while updating the servers config. This should not happen, please contact the bot developer.")
		return
	}

	bot.ChannelMessageSend(m.ChannelID, "Guild configuration updated successfully")
}

func handleDMMessage(s *discordgo.Session, m *discordgo.MessageCreate, userID string) {

	sendMessage := func(channelID string, thread *db.ModMailThread) {
		var err error

		embed := &discordgo.MessageEmbed{
			Description: m.Content,
			Timestamp:   time.Now().Format(time.RFC3339),
			Author: &discordgo.MessageEmbedAuthor{
				Name:    fmt.Sprintf("%s#%s", m.Author.Username, m.Author.Discriminator),
				IconURL: m.Author.AvatarURL("128x128"),
			},
			Footer: &discordgo.MessageEmbedFooter{
				Text: m.Author.ID,
			},
		}

		for _, a := range m.Attachments {
			name := a.Filename
			if strings.HasSuffix(name, ".png") ||
				strings.HasSuffix(name, ".jpg") ||
				strings.HasSuffix(a.Filename, ".gif") {
				if embed.Image != nil {
					embed.Description += "\n" + a.URL
					continue
				}
				embed.Image = &discordgo.MessageEmbedImage{
					URL: a.URL,
				}
			} else {
				embed.Description += "\n" + a.URL
			}

		}

		_, err = s.ChannelMessageSendEmbed(channelID, embed)

		if err != nil && err.(*discordgo.RESTError).Response.StatusCode == 404 {
			db.DeleteModMailThread(thread)

			s.ChannelMessageSend(m.ChannelID, "Modmail channel has been deleted. Send a new message to create a new thread.")

			return
		}

		if err != nil {
			s.ChannelMessageSend(m.ChannelID, "An unknown error occurred.")
		}

		db.CreateModMailMessage(&db.ModMailMessage{
			MessageID: m.ID,
			ChannelID: m.ChannelID,
			ThreadID:  thread.ID,
			Content:   m.Content,
		})
	}

	thread, _ := db.GetModMailThreadByUserID(userID)

	if thread != nil {
		channelID := thread.ChannelID

		_, err := m.ContentWithMoreMentionsReplaced(s)

		if err != nil {
			return
		}

		sendMessage(channelID, thread)

		return
	}

	guildID := "585606083897458691"

	config, err := db.GetGuildConfig(guildID)

	if err != nil {
		s.ChannelMessageSend(m.ChannelID, "Could not get the config for this server")
		return
	}

	if config.ModmailCategoryID == "" {
		s.ChannelMessageSend(m.ChannelID, "Server does not have modmail setup")
	}

	channel, err := bot.GuildChannelCreateComplex(
		guildID,
		discordgo.GuildChannelCreateData{
			Name:     fmt.Sprintf("%s-%s", m.Author.Username, m.Author.Discriminator),
			Topic:    m.Content,
			Type:     discordgo.ChannelTypeGuildText,
			ParentID: config.ModmailCategoryID,
		},
	)

	if err != nil {
		s.ChannelMessageSend(m.ChannelID, "An unkown error occured while creating a thread for this server")
	}

	thread, err = db.CreateModMailThread(guildID, channel.ID, m.Author.ID)

	if err != nil {
		s.ChannelMessageSend(m.ChannelID, "An unknown error occured while creating this thread. Please contact the bot developer.")
		s.ChannelMessageSend(channel.ID, "An unknown error occured while creating this thread. Please contact the bot developer.")
		return
	}

	sendMessage(channel.ID, thread)
}

func handleGuildMessage(s *discordgo.Session, m *discordgo.MessageCreate, userID string) {

	thread, err := db.GetModMailThreadByChannelID(m.ChannelID)

	if err != nil {
		return
	}

	guild, err := s.Guild(m.GuildID)

	if err != nil {
		return
	}

	embed := &discordgo.MessageEmbed{
		Description: m.Content,
		Author: &discordgo.MessageEmbedAuthor{
			Name:    guild.Name,
			IconURL: guild.IconURL(),
		},
		Timestamp: time.Now().Format(time.RFC3339),
		Footer: &discordgo.MessageEmbedFooter{
			Text: m.Author.ID,
		},
	}

	for _, a := range m.Attachments {
		name := a.Filename
		if strings.HasSuffix(name, ".png") ||
			strings.HasSuffix(name, ".jpg") ||
			strings.HasSuffix(a.Filename, ".gif") {
			if embed.Image != nil {
				embed.Description += "\n" + a.URL
				continue
			}
			embed.Image = &discordgo.MessageEmbedImage{
				URL: a.URL,
			}
		} else {
			embed.Description += "\n" + a.URL
		}

	}

	c, err := s.UserChannelCreate(thread.UserID)

	if err != nil {
		s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("Could not send a message to <@%s>", thread.UserID))
	}

	_, err = s.ChannelMessageSendEmbed(c.ID, embed)

	if err != nil {
		s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("Could not send a message to <@%s>", thread.UserID))
	}

	if err != nil {
		s.ChannelMessageSend(m.ChannelID, "An unknown error occurred.")
	}

	db.CreateModMailMessage(&db.ModMailMessage{
		MessageID: m.ID,
		ChannelID: m.ChannelID,
		ThreadID:  thread.ID,
		Content:   m.Content,
	})

}
