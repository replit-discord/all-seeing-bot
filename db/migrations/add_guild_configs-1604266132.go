package migrations

import (
	"github.com/go-gormigrate/gormigrate/v2"
	"gorm.io/gorm"
)

type guildConfig struct {
	ID      int    `json:"id"       gorm:"primaryKey"`
	GuildID string `json:"guild_id" gorm:"unique;not null"`
	Config  []byte `json:"config"   gorm:"not null"  sql:"type:jsonb"`
}

var addGuildConfigs = &gormigrate.Migration{
	ID: "1604266132",
	Migrate: func(tx *gorm.DB) error {
		return tx.AutoMigrate(&guildConfig{})
	},
	Rollback: func(tx *gorm.DB) error {
		return tx.Migrator().DropTable("guild_configs")
	},
}
