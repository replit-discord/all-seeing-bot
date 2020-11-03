package util

import (
	"regexp"
)

// DevIDs is  a list of users with access to dev commands
var DevIDs = [...]string{"487258918465306634"}

// MentionRegex is the regex used to find mentions of any type
var MentionRegex *regexp.Regexp

// RoleMentionRegex is the regex used to find role mentions
var RoleMentionRegex *regexp.Regexp

// UserMentionRegex is the regex used to find user mentions
var UserMentionRegex *regexp.Regexp

// ChannelMentionRegex is the regex used to find user mentions
var ChannelMentionRegex *regexp.Regexp

// NumberRegex is just \d+
var NumberRegex *regexp.Regexp

func init() {
	MentionRegex = regexp.MustCompile("<(@[!&])|(#)?\\d+>")
	RoleMentionRegex = regexp.MustCompile("<@&\\d+>")
	UserMentionRegex = regexp.MustCompile("<@!?\\d+>")
	ChannelMentionRegex = regexp.MustCompile("<#\\d+>")
	NumberRegex = regexp.MustCompile("\\d+")
}
