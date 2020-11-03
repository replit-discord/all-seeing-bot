package migrations

import (
	"github.com/go-gormigrate/gormigrate/v2"
	"gorm.io/gorm"
)

type modMailThread struct {
	gorm.Model
	GuildID  string            `json:"guild_id"   gorm:"<-:create;not null"`
	UserID   string            `json:"user_id"    gorm:"<-:create; not null"`
	Messages []*modMailMessage `gorm:"foreignKey:ThreadID"`
}

type modMailMessage struct {
	gorm.Model
	MessageID string         `json:"guild_id"   gorm:"<-:create;not null; unique"`
	ChannelID string         `json:"channel_id" gorm:"<-:create;not null"`
	ThreadID  uint           `json:"thread_id"  gorm:"<-:create;not null"`
	Thread    *modMailThread `gorm:"foreignKey:ThreadID"`
}

var addModMail = &gormigrate.Migration{
	ID: "1604417825",
	Migrate: func(tx *gorm.DB) error {
		err := tx.AutoMigrate(&modMailThread{})
		if err != nil {
			return err
		}
		return tx.AutoMigrate(&modMailMessage{})
	},
	Rollback: func(tx *gorm.DB) error {
		err := tx.Migrator().DropTable("mod_mail_threads")
		if err != nil {
			return err
		}
		return tx.Migrator().DropTable("mod_mail_messages")
	},
}
