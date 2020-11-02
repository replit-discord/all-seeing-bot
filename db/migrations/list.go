package migrations

import "github.com/go-gormigrate/gormigrate/v2"

var migrations = []*gormigrate.Migration{
	addGuildConfigs,
	addGuildPermissions,
}
