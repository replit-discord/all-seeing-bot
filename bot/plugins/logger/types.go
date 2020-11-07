package logger

import "github.com/bwmarrin/discordgo"

// Config is a config used by other plugins that the logger uses to identify the plugin
// in the embeds for the logs.
type Config struct {
	// The name of the plugin
	Name string

	// The color code for the plugin
	Color int
}

// LogCreate is the type used for log creation
type LogCreate struct {
	// Author is the author field for the embed
	Author *discordgo.MessageEmbedAuthor

	// Config is config of the plugin creating the log
	Config *Config

	// Fields are the embed fields
	Fields []*discordgo.MessageEmbedField

	// Message is the description of the log embed
	Message string
}
