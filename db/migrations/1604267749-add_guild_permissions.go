package migrations

import (
	"github.com/go-gormigrate/gormigrate/v2"
	"gorm.io/gorm"
)

type guildPermission struct {
	gorm.Model
	GuildID     string `json:"guild_id"   gorm:"<-:create;not null"`
	ChannelID   string `json:"channel_id" gorm:"<-:create;"`
	RoleID      string `json:"role_id"    gorm:"unique; <-:create; not null"`
	Permissions []byte `json:"permissions"`
}

var addGuildPermissions = &gormigrate.Migration{
	ID: "1604267749",
	Migrate: func(tx *gorm.DB) error {
		return tx.AutoMigrate(&guildPermission{})
	},
	Rollback: func(tx *gorm.DB) error {
		return tx.Migrator().DropTable("guild_permissions")
	},
}
