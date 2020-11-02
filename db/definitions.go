package db

import (
	"time"

	"database/sql/driver"
	"encoding/json"

	// postgres driver for go
	_ "github.com/lib/pq"
	"gorm.io/gorm"
)

// GuildConfigType is the type for guild config objects
type GuildConfigType struct {
	Prefix   string `json:"prefix"`
	MuteRole string `json:"muterole"`
}

// Value probably does sometihng
func (j GuildConfigType) Value() (driver.Value, error) {
	valueString, err := json.Marshal(j)
	return string(valueString), err
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
