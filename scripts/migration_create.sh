#!/bin/bash

cd ./db/migrations
echo Enter the snake_case name for the migration.
read NAME
export ID=$(date +%s)

cat >"$NAME-$ID.go" <<EOF
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


cat >"list.go" <<EOF
package migrations

import "github.com/go-gormigrate/gormigrate/v2"

var migrations = []*gormigrate.Migration{
$(for f in $(ls --ignore migrations.go --ignore list.go)
do
    echo "	$(echo $f |
        grep -m 1 -a --regexp='[^-]*' -o |
        head -n 1 |
        sed -r 's/_([a-z])/\U\1/gi' |
        sed -r 's/^([A-Z])/\l\1/'
    ),"
done )
}
EOF

echo Migration created in db/migrations/$NAME-$ID.go
