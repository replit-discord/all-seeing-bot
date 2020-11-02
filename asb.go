package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/repl-it-discord/all-seeing-bot/bot"
	"github.com/repl-it-discord/all-seeing-bot/db"
)

func main() {
	db.Connect()

	fmt.Println("Connected to DB")

	go bot.Run()
	f, _ := os.Create("asb.lock")

	defer f.Close()

	sigs := make(chan os.Signal, 1)

	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	<-sigs
	db.Close()
	bot.Kill()

	os.Remove(f.Name())
}
