// +build file

package main

import (
	"fmt"
	"io/ioutil"
	"os"
)

func printHelp() {
	fmt.Println("Just a quick lil binary I made.  3 args:")
	fmt.Println()
	fmt.Println("1) Banned word- this is the word that you are testing for the program to detect.")
	fmt.Println()
	fmt.Println("2) file- the file you want to test. ")
	fmt.Println()
	fmt.Println("3) Expected- wether or not it should be flagged, the test returns true if a banned word is detected. 1 for true 0 for false.")
	os.Exit(1)
}

func main() {

	if len(os.Args) != 4 {
		printHelp()
	}

	banned = append(banned, os.Args[1])

	bytes, err := ioutil.ReadFile(os.Args[2])
	if err != nil {
		panic(err)
	}
	fmt.Println(len(string(bytes)))
	exp := os.Args[3] != "0"
	test(string(bytes), exp)
}
