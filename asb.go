package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/repl-it-discord/all-seeing-bot/bot"
	"github.com/repl-it-discord/all-seeing-bot/db"
)

const lockFilePath = "/tmp/asb.lock"

func main() {
	defer func() {

		os.Remove(lockFilePath)
		if r := recover(); r != nil {
			log.Print("Panic occurred:", r)
		}
	}()
	log.SetFlags(log.Ldate | log.Llongfile | log.Ltime)

	now := time.Now().Local().Format("02-01-2006")

	f, err := os.OpenFile(
		fmt.Sprintf("logs/%s.log", now),
		os.O_WRONLY|os.O_CREATE|os.O_APPEND,
		0644,
	)

	if err != nil {
		panic(err)
	}

	log.SetOutput(f)
	db.Connect()

	fmt.Println("Connected to DB")

	go bot.Run()
	f, _ = os.Create(lockFilePath)

	defer f.Close()

	sigs := make(chan os.Signal, 1)

	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	<-sigs
	db.Close()
	bot.Kill()
}
