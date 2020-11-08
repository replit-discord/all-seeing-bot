package main

import (
	"fmt"
	"io"
	"log"
	"os"
	"os/signal"
	"runtime/debug"
	"syscall"
	"time"

	"github.com/repl-it-discord/all-seeing-bot/bot"
	"github.com/repl-it-discord/all-seeing-bot/db"
)

const lockFilePath = "/tmp/asb.lock"

func close() {
	defer func() {
		if r := recover(); r != nil {
			log.Print("Unable to close cleanly", r)
			log.Print(string(debug.Stack()))
		}
	}()

	db.Close()
	bot.Kill()
}

type logger struct {
}

var loguout io.Writer

func ensureLogFile() {
	if os.Getenv("LOG_LEVEL") == "1" {
		log.SetOutput(os.Stderr)
		return
	}

	setLogs := func() {
		f, err := os.OpenFile(
			fmt.Sprintf("logs/%s.log", time.Now().Local().Format("01-02-2006")),
			os.O_WRONLY|os.O_CREATE|os.O_APPEND,
			0644,
		)

		if err != nil {
			panic(err)
		}

		if os.Getenv("LOG_LEVEL") == "1" {
			log.SetOutput(f)
		} else {
			log.SetOutput(io.MultiWriter(f, os.Stderr))
		}
	}

	setLogs()

	go func() {
		for {
			y, m, d := time.Now().Local().Date()
			nextDay := time.Date(y, m, d+1, 0, 0, 0, 0, time.Local)

			time.Sleep(time.Until(nextDay))
			setLogs()
		}
	}()

}

func main() {
	defer func() {
		if r := recover(); r != nil {
			close()
			log.Print("Panic:", r)
			log.Print(string(debug.Stack()))
		}
		os.Remove(lockFilePath)
	}()
	log.SetFlags(log.Ldate | log.Llongfile | log.Ltime)

	ensureLogFile()

	db.Connect()

	fmt.Println("Connected to DB")

	bot.Run()
	f, _ := os.Create(lockFilePath)

	defer f.Close()

	sigs := make(chan os.Signal, 1)

	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	<-sigs
	close()
}
