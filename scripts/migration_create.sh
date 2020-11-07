#!/bin/bash

cd ./db/migrations
echo Enter the snake_case name for the migration.
read NAME
export ID=$(date +%s)

cat >"$ID-$NAME.go" <<EOF
package migrations

import (
    "errors"

	"github.com/go-gormigrate/gormigrate/v2"
	"gorm.io/gorm"
)


var $(
    echo $NAME | sed -r 's/_([a-z])/\U\1/gi' |
    sed -r 's/^([A-Z])/\l\1/'
) = &gormigrate.Migration{
    ID: "$ID",
    Migrate: func (tx *gorm.DB) error {
        return errors.New("Migration code has not yet been created")
    },
    Rollback: func(tx *gorm.DB) error {
        return errors.New("Migration code has not yet been created")
    },
}

EOF


echo Migration created in db/migrations/$NAME-$ID.go
echo Don\'t forget to add it to the list