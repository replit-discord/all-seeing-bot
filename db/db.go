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

// ErrRecordExists is the error if a record being created already exists
var ErrRecordExists = errors.New("Record already exists")

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

// GetDB returns the psql DB client
func GetDB() *gorm.DB {
	return db
}

// GetStore returns the redis client
func GetStore() *redis.Client {
	return store
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

func delete(key string) {
	store.Del(store.Context(), key)
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
func GetGuildPermissions(guildID string) ([]*GuildPermission, error) {
	key := guildID + "-permissions"
	var err error

	if guildID == "" {
		return nil, errors.New("no guild id provided")
	}

	rows := []*GuildPermission{}

	err = fetch(key, rows)

	if err == nil {
		defer cache(key, rows, time.Hour)

		return rows, nil
	}

	db.Where(&GuildPermission{GuildID: guildID}).Find(&rows)

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

// GetModMailThreadByUserID is used to try and find a modmail thread by the id of the user the thread belongs to
func GetModMailThreadByUserID(userID string) (*ModMailThread, error) {
	key := userID + "-thread"
	thread := &ModMailThread{
		UserID: userID,
	}

	err := fetch(key, thread)

	if err == nil {
		return thread, nil
	}

	tx := db.Where(thread).First(thread)

	if tx.Error != nil {
		return nil, tx.Error
	}

	if thread == nil {
		return nil, errors.New("thread not found")
	}

	return thread, cache(key, thread, time.Hour)
}

// GetModMailThreadByChannelID is used to try and find a modmail thread by the channel id that belong to the thread
func GetModMailThreadByChannelID(channelID string) (*ModMailThread, error) {
	key := channelID + "-thread"
	thread := &ModMailThread{
		ChannelID: channelID,
	}

	err := fetch(key, thread)

	if err == nil {
		return thread, nil
	}

	tx := db.Where(thread).First(thread)

	if tx.Error != nil {
		return nil, tx.Error
	}

	return thread, cache(key, thread, time.Hour)
}

// DeleteModMailThread is used to delete a modmail thread
func DeleteModMailThread(thread *ModMailThread) {
	key := thread.UserID + "-thread"

	delete(key)

	db.Delete(thread)
}

// CreateModMailThread is used to create a modmail thread
func CreateModMailThread(guildID, channelID, userID string) (*ModMailThread, error) {
	thread, _ := GetModMailThreadByUserID(userID)

	if thread != nil {
		return thread, ErrRecordExists
	}

	thread = &ModMailThread{
		GuildID:   guildID,
		ChannelID: channelID,
		UserID:    userID,
	}

	tx := db.Save(thread)

	return thread, tx.Error
}

// CreateModMailMessage is used to create a record for a modmail message
func CreateModMailMessage(m *ModMailMessage) (*ModMailMessage, error) {
	return m, db.Create(m).Error
}

// CreateGuildMuteRecord is used to create a mute record
func CreateGuildMuteRecord(m *GuildMute) (*GuildMute, error) {
	return m, db.Create(m).Error
}

// GetMute is used to fetch a mute record
func GetMute(m *GuildMute) error {
	return db.Where(m).Find(m).Error
}

// GetMutes is used to fetch all of the mutes in the db
func GetMutes() ([]*GuildMute, error) {
	var mutes []*GuildMute
	return mutes, db.Find(&mutes).Error
}

// DeleteMute is used to delete a guildMute record
func DeleteMute(m *GuildMute) error {
	return db.Where(m).Delete(m).Error
}
