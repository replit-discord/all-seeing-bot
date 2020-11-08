package db

import (
	"time"

	"database/sql/driver"
	"encoding/json"

	// postgres driver for go
	_ "github.com/lib/pq"
	"gorm.io/gorm"
)

type whereParams map[string]interface{}

// GuildConfigType is the type for guild config objects
type GuildConfigType struct {
	Prefix            string `json:"prefix"`
	MuteRole          string `json:"muterole"`
	ModmailCategoryID string `json:"mod_mail_category_id"`
	LogChannel        string `json:"log_channel"`
}

// Value probably does sometihng
func (j GuildConfigType) Value() (driver.Value, error) {
	valueString, err := json.Marshal(j)
	return valueString, err
}

// Scan is used to scan haha great desc
func (j *GuildConfigType) Scan(value interface{}) error {
	if err := json.Unmarshal(value.([]byte), &j); err != nil {
		return err
	}
	return nil
}

// BannedWord is the type for banword rows
type BannedWord struct {
	ID          int       `json:"id"`
	GuildID     string    `json:"guild_id"`
	Word        string    `json:"word"`
	Paranoia    int       `json:"paranoia"`
	TimeDeleted time.Time `json:"time_deleted"`
}

// GuildConfig is the type for the rows containing guild configs
type GuildConfig struct {
	ID      int             `json:"id"       gorm:"primaryKey"`
	GuildID string          `json:"guild_id" gorm:"unique;not null"`
	Config  GuildConfigType `json:"config"   gorm:"not null"  sql:"type:jsonb"`
}

// GuildPermission is the type for permission rows
type GuildPermission struct {
	GuildID     string `json:"guild_id"   gorm:"<-:create;not null"`
	ChannelID   string `json:"channel_id" gorm:"<-:create;not null"`
	RoleID      string `json:"role_id"    gorm:"unique; <-:create; not null"`
	Permissions []byte `json:"permissions"`
	gorm.Model
}

// ModMailThread is the type for rows in mod_mail_threads
type ModMailThread struct {
	gorm.Model
	GuildID   string            `json:"guild_id"     gorm:"<-:create;not null"`
	ChannelID string            `json:"channel_id"   gorm:"<-:create;not null"`
	UserID    string            `json:"user_id"      gorm:"<-:create;not null"`
	Messages  []*ModMailMessage `gorm:"foreignKey:ThreadID"`
}

// ModMailMessage is the type for the sql rows for mod mail messages
type ModMailMessage struct {
	gorm.Model
	Content   string         `json:"content"    gorm:"not null;"`
	MessageID string         `json:"guild_id"   gorm:"<-:create;not null; unique"`
	ChannelID string         `json:"channel_id" gorm:"<-:create;not null"`
	ThreadID  uint           `json:"thread_id"  gorm:"<-:create;not null"`
	Thread    *ModMailThread `gorm:"foreignKey:ThreadID"`
}

// GuildMute is the type for sql records / rows used to track mutes + their expirations
type GuildMute struct {
	gorm.Model
	GuildID   string    `json:"guild_id"     gorm:"<-:create;not null"`
	ExpiresAt time.Time `json:"expires_at"   gorm:"<-:create;"`
	UserID    string    `json:"user_id"      gorm:"<-:create;not null"`
}

// HelpSession is a help session for the bot
type HelpSession struct {
	MessageID string `json:"message_id"`
	Plugin    string `json:"plugin"`
	Page      int    `json:"page"`
}
