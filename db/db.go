package db

import (
	"encoding/json"
	"errors"
	"fmt"
	"time"

	redis "github.com/go-redis/redis/v8"
	"github.com/repl-it-discord/all-seeing-bot/db/migrations"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func chk(err error) {
	if err != nil {
		panic(err)
	}
}

var db *gorm.DB
var store *redis.Client

var baseConfig = GuildConfigType{Prefix: "?"}

const (
	host   = "postgres"
	port   = 5432
	user   = "allawesome497"
	dbname = "allseeingbot"
)

// Connect is used to connect to the DB
func Connect() {
	var err error
	dsn := fmt.Sprintf("host=%s port=%d user=%s "+
		"dbname=%s sslmode=disable",
		host, port, user, dbname)
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})

	chk(err)

	migrations.Migrate(db)

	store = redis.NewClient(&redis.Options{
		Addr: "redis:6379",
	})

	chk(err)

}

// Close is used to close the connetion to the DB
func Close() {
	store.Close()
}

func cache(key string, v interface{}, expiration time.Duration) error {
	val, err := json.Marshal(v)

	if err != nil {
		return err
	}

	store.Set(store.Context(), key, string(val), expiration)

	return nil
}

func fetch(key string, v interface{}) error {
	res := store.Get(store.Context(), key)

	val, err := res.Result()

	if err != nil {
		return err
	}

	return json.Unmarshal([]byte(val), v)
}

// GetGuildConfig is used to get the config for a guild
func GetGuildConfig(guildID string) (*GuildConfigType, error) {

	var err error

	if guildID == "" {
		return &baseConfig, err
	}

	configRow := &GuildConfig{}

	err = fetch(guildID+"-config", configRow)

	if err == nil {
		// Reset the expiration
		defer cache(guildID+"-config", configRow, time.Hour)

		return &configRow.Config, err
	}

	res := db.Where(&GuildConfig{GuildID: guildID}).First(configRow)

	if res.Error != nil {

		// tx, err := db.Mo
		res := db.Create(&GuildConfig{
			GuildID: guildID,
			Config:  baseConfig,
		})

		if res.Error != nil {
			return nil, res.Error
		}

		return GetGuildConfig(guildID)
	}

	err = cache(guildID+"-config", configRow, time.Hour)

	if err != nil {
		return nil, err
	}

	return &configRow.Config, err
}

// SetGuildConfig is used to set the config of a guild
func SetGuildConfig(guildID string, config *GuildConfigType) error {
	// This will create a config if we don't already have one
	GetGuildConfig(guildID)

	var configRow = &GuildConfig{GuildID: guildID}

	res := db.Where(&GuildConfig{GuildID: guildID}).First(configRow)

	if res.Error != nil {
		return res.Error
	}

	configRow.Config = *config

	res = db.Save(configRow)

	if res.Error != nil {
		return res.Error
	}

	return cache(guildID+"-config", configRow, time.Hour)
}

// GetGuildPermissions is used to get permissions for a guild
func GetGuildPermissions(guildID string) (*[]*GuildPermission, error) {
	key := guildID + "-permissions"
	var err error

	if guildID == "" {
		return nil, errors.New("no guild id provided")
	}

	rows := &[]*GuildPermission{}

	err = fetch(key, rows)

	if err == nil {
		defer cache(key, rows, time.Hour)

		return rows, nil
	}

	db.Where(&GuildPermission{GuildID: guildID}).Find(rows)

	err = cache(key, rows, time.Hour)

	return rows, err
}

// SetGuildPermissions is used to set permissions
func SetGuildPermissions(guildID string, r, channelID *string, permissions []byte) error {
	key := guildID + "-permissions"
	var roleID string
	if r == nil {
		roleID = guildID
	}

	perms := &GuildPermission{}

	if channelID == nil {
		perms = &GuildPermission{
			GuildID: guildID,
			RoleID:  roleID,
		}
	} else {
		perms = &GuildPermission{
			GuildID:   guildID,
			RoleID:    roleID,
			ChannelID: *channelID,
		}
	}

	db.First(perms)

	perms.Permissions = permissions

	resp := db.Save(perms)

	if resp.Error != nil {
		return resp.Error
	}

	store.Del(store.Context(), key)

	return nil
}
