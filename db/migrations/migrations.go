package migrations

import (
	"github.com/go-gormigrate/gormigrate/v2"
	"gorm.io/gorm"
)

var migrations = []*gormigrate.Migration{
	addGuildConfigs,
	addGuildPermissions,
	addModMail,
	addGuildMutes,
}

// Migrate runs the db migrations
func Migrate(db *gorm.DB) {
	m := gormigrate.New(db, gormigrate.DefaultOptions, migrations)
	// m.RollbackLast()
	if err := m.Migrate(); err != nil {
		panic(err)
	}
}
