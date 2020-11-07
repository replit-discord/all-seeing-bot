package background

import (
	"log"
	"time"

	"github.com/repl-it-discord/all-seeing-bot/bot/plugins"
	"github.com/repl-it-discord/all-seeing-bot/bot/types"
)

// Task is a task which should be ran at an interval.
type Task struct {
	// Interval is the interval at which the task should be ran at
	Interval time.Duration

	// Run is the function to be called at for the task
	Run func()

	ticker *time.Ticker

	done chan bool
}

var tasks = []*Task{}

var plugin = &types.Plugin{Close: close}

func close() {
	for _, t := range tasks {
		t.ticker.Stop()
		t.done <- true
	}
}

// RegisterTask is used to register a background task
func RegisterTask(name string, task Task) {
	task.ticker = time.NewTicker(task.Interval)

	go func() {
		panicSafeExec := func() {
			defer func() {
				if r := recover(); r != nil {
					log.Print("err while executing "+name+":", r)
				}
			}()

			task.Run()
		}

		for {
			select {
			case <-task.ticker.C:
				panicSafeExec()
				break
			case <-task.done:
				return
			}
		}
	}()
}

func init() {
	plugins.Register(plugin)
}
