export GOMAXPROCS=2



run: build
	@./all-seeing-bot

build:
	@go build

create-migration:
	@./scripts/migration_create.sh

