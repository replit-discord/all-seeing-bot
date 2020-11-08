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

// ParseMember is used to get a user from their id, username, mention etc.
func ParseMember(s *discordgo.Session, guildID, user string) (*discordgo.Member, error) {
	if UserMentionRegex.MatchString(user) {
		user = NumberRegex.FindString(user)

		return s.GuildMember(guildID, user)
	} else if !NonNumberRegex.MatchString(user) {
		return s.GuildMember(guildID, user)
	} else {
		guild, err := s.State.Guild(guildID)

		if err != nil {
			return nil, err
		}

		discrim := discriminatorRegex.FindString(user)

		if discrim != "" && strings.HasPrefix(user, discrim) {
			for _, m := range guild.Members {
				if m.User.Username+"#"+m.User.Discriminator == user {
					return m, nil
				}
			}

			user = strings.ToLower(user)

			for _, m := range guild.Members {
				if strings.ToLower(m.User.Username)+"#"+m.User.Discriminator == user {
					return m, nil
				}
			}

			return nil, errors.New("User not found")
		}

		for _, m := range guild.Members {
			if m.User.Username == user {
				return m, nil

			}
		}

		user = strings.ToLower(user)

		for _, m := range guild.Members {
			if strings.ToLower(m.User.Username) == user {
				return m, nil
			}
		}

		// down to nicknames, at this point screw capitalization

		for _, m := range guild.Members {
			if m.Nick == "" {
				continue
			}
			if strings.ToLower(m.Nick) == user {
				return m, nil
			}
		}

		return nil, errors.New("User not found")
	}
}

// ParseChannel is used to get a user from their id, username, mention etc.
func ParseChannel(s *discordgo.Session, guildID, channel string) (*discordgo.Channel, error) {
	if ChannelMentionRegex.MatchString(channel) {
		channelID := NumberRegex.FindString(channel)

		return s.State.Channel(channelID)
	} else if !NonNumberRegex.MatchString(channel) {
		return s.State.Channel(channel)
	} else {
		guild, err := s.State.Guild(guildID)

		if err != nil {
			return nil, err
		}

		channel = strings.ToLower(channel)

		for _, c := range guild.Channels {
			if strings.ToLower(c.Name) == channel {
				return c, nil
			}
		}

		return nil, errors.New("Channel not found")
	}
}

// RepairArgs is used to return an array of arguments back to its original state.
func RepairArgs(args []string) string {
	result := ""

	for _, v := range args {
		if strings.Contains(v, " ") {
			result += ` "` + v + `"`
		} else {
			result += " " + v
		}
	}

	return result
}

// GetAuthor is used to return an embed author to depict a user
func GetAuthor(u *discordgo.User) *discordgo.MessageEmbedAuthor {
	return &discordgo.MessageEmbedAuthor{
		Name:    u.Username + "#" + u.Discriminator,
		IconURL: u.AvatarURL("128x128"),
	}
}

// Bold returns the bold version of a string
func Bold(in string) string {
	return "**" + in + "**"
}

// CapitalizeFirst capitalizes the first letter of a string
func CapitalizeFirst(in string) string {
	return strings.ToUpper(string(in[0])) + in[1:]
}
