package migrations

import (
	"time"

	"github.com/go-gormigrate/gormigrate/v2"
	"gorm.io/gorm"
)

type guildMute struct {
	gorm.Model
	GuildID   string    `json:"guild_id"     gorm:"<-:create;not null"`
	ExpiresAt time.Time `json:"expires_at"   gorm:"<-:create;"`
	UserID    string    `json:"user_id"      gorm:"<-:create;not null"`
}

var addGuildMutes = &gormigrate.Migration{
	ID: "1604596731",
	Migrate: func(tx *gorm.DB) error {
		return tx.AutoMigrate(&guildMute{})
	},
	Rollback: func(tx *gorm.DB) error {
		return tx.Migrator().DropTable("guild_mutes")
	},
}
