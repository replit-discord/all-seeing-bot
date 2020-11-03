package util

import (
	"errors"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/repl-it-discord/all-seeing-bot/util/perms"
)

// IsAdmin returns whether the author of a message is an admin or not
func IsAdmin(s *discordgo.Session, m *discordgo.Message) bool {
	permissions, err := s.State.UserChannelPermissions(m.Author.ID, m.ChannelID)

	if err != nil {
		return false
	}

	return permissions&int(perms.Administrator) > 0
}

// HasAnyPermissionsIn returns whether the author of a message has the permissions listed.
func HasAnyPermissionsIn(s *discordgo.Session, m *discordgo.Message, permissionNodes ...perms.DiscordPermission) bool {
	permissions, err := s.State.UserChannelPermissions(m.Author.ID, m.ChannelID)

	if err != nil {
		return false
	}

	var requiredPerms = 0

	for _, perm := range permissionNodes {
		requiredPerms |= int(perm)
	}

	return permissions&requiredPerms > 0
}

// ParseArgs is used to parse arguments from the provided string
func ParseArgs(raw string) []string {
	args := []string{}
	current := ""
	ignoreNextQuote := false
	isQuoted := false
	quotesUsedCount := 0
	quoteCount := 0
	quotePos := 0

	for _, c := range raw {
		if c == '"' {
			quoteCount++
		}
	}

	for i, c := range raw {
		switch c {
		case ' ':
			if isQuoted {
				if ignoreNextQuote {
					current += "\\"
				}
				current += string(c)
				ignoreNextQuote = false
				break
			}

			args = append(args, current)
			current = ""
			ignoreNextQuote = false
			break
		case '"':
			quotesUsedCount++
			if !isQuoted && quotesUsedCount == quoteCount {
				if ignoreNextQuote {
					ignoreNextQuote = false
					current += "\\"
				}
				current += string(c)

				break
			}

			if ignoreNextQuote {
				current += string(c)
				ignoreNextQuote = false
				break
			}
			quotePos = i
			isQuoted = !isQuoted
			break
		case '\\':
			if ignoreNextQuote {
				ignoreNextQuote = false
				current += "\\\\"
				break
			}

			ignoreNextQuote = true
			break
		default:
			if ignoreNextQuote {
				ignoreNextQuote = false
				current += "\\"
			}
			current += string(c)
		}
	}

	if current != "" {
		args = append(args, current)
	}

	if isQuoted {
		charCount := 0
		for i, arg := range args {
			if quotePos-charCount >= len(arg) {
				charCount += len(arg)
				continue
			}

			index := quotePos - charCount

			args[i] = arg[:index] + "\"" + arg[index:]
		}
	}

	return args
}

// ParseMention parses a string and returns the mentioned object and whether a user was found or not.
func ParseMention(s *discordgo.Session, guildID, m string, v interface{}) error {

	if !MentionRegex.MatchString(m) {
		return errors.New("invalid mention")
	}

	switch v.(type) {
	case *discordgo.Role:
		if !strings.HasPrefix(m, "<@&") {
			return errors.New("invalid role mention")
		}
		roleID := m[3 : len(m)-1]

		role, err := s.State.Role(guildID, roleID)

		v = role
		return err
	case *discordgo.Channel:
		if !strings.HasPrefix(m, "<@#") {
			return errors.New("invalid channel mention")
		}
		channelID := m[3 : len(m)-1]

		channel, err := s.State.Channel(channelID)

		v = channel
		return err
	}

	return nil
}
