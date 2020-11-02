export GOMAXPROCS=2



run: build
	@./all-seeing-bot

build:
	@go build

migrate: 
	@if [ $(IS_DOCKER_APP) == yes ]
	@then
	@	

create-migration:
	@./scripts/migration_create.sh

