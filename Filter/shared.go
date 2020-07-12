// +build shared

package main

import (
	"fmt"
	"os"

	"strings"
)

func printHelp() {
	fmt.Println("Just a quick lil binary I made.  3 args:")
	fmt.Println()
	fmt.Println("1) Banned word- this is the word that you are testing for the program to detect.")
	fmt.Println()
	fmt.Println("2) Paranoid- Wether paranoia is enabled for the word.  Banned word is found more along with more potential for false positives. true or t for true")
	fmt.Println()
	fmt.Println("3) String- the string you want to test. ")
	fmt.Println()
	fmt.Println("4) Expected- wether or not it should be flagged, the test returns true if a banned word is detected. 1 for true 0 for false.")
	os.Exit(1)
}

func init() {
	banned = make(map[string]bool)
}

func main() {
	if len(os.Args) != 5 {
		printHelp()
	}
	if strings.ToLower(os.Args[2]) == "true" || strings.ToLower(os.Args[2]) == "t" {
		banned[os.Args[1]] = true
	} else {
		banned[os.Args[1]] = false
	}
	// if os.Args[2]
	// fmt.Println(banned)
	exp := os.Args[4] != "0"

	test(os.Args[3], exp)
}
