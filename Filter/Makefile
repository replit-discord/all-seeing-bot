
main-%:
	go build -o main -tags=$(*)

# shared-

build: 
	go build -o libfilter.so -buildmode c-shared -tags c

# .PHONY: run
run: main-dev
	./main


update-conv:
	@python3 minnify.py
	@go-bindata conv.json
	@python3 prettify.py


help:
	@echo bruh