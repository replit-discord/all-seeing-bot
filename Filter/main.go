package main

/*
#include <stdbool.h>

struct word {
	char paranoid;
	char *word;
};
*/
import "C"

import (
	"bytes"
	"encoding/json"
	"fmt"
	"regexp"
	"strings"

	"github.com/fatih/color"
)

var banned = map[string]bool{
	"ass":         false,
	"cock":        false,
	"nig" + "ger": false,
	"penis":       false,
	"shit":        true,
	"hoist":       false,
}

var count = 0

var ignoreRegex *regexp.Regexp

type char struct {
	Char     string
	Possible []string       `json:"Types"`
	Regex    *regexp.Regexp `json:"-"`
}

var replaceDict []char
var ready bool

func init() {
	ready = true
	dat, err := Asset("conv.json")
	if err != nil {
		panic(err)
	}
	f := bytes.NewBuffer(dat)

	dec := json.NewDecoder(f)

	dec.Decode(&replaceDict)

	for i := 0; i < len(replaceDict); i++ {
		c := &replaceDict[i]

		for pos := 0; pos < len(c.Possible); pos++ {
			possible := c.Possible
			if possible[pos] == "" {
				newPossible := make([]string, len(c.Possible))
				copied := copy(newPossible, c.Possible[:pos])
				copy(newPossible[copied:], c.Possible[pos:])
				c.Possible = newPossible
			}
		}

		exp, err := regexp.Compile("[" + strings.Join(c.Possible, "") + "]")
		if err != nil {
			panic(err)
		}

		c.Regex = exp
	}

	ignoreRegex, err = regexp.Compile(strings.Join(ignored, "|"))
	if err != nil {
		panic(err)
	}
}

//export check
func check(rawStr *C.char, rawWords []*C.struct_word) bool {

	str := C.GoString(rawStr)

	words := make(map[string]uint8)

	for _, w := range rawWords {
		words[strings.ToLower(C.GoString(w.word))] = uint8(w.paranoid)
	}

	// This should make sure that we dont get any invalid regex
	var banned = make(map[string]string)
	for v, p := range words {
		if p == 0 {
			banned[v] = v
			continue
		}
		for _, p := range prefixes {
			for _, s := range suffixes {
				banned[p+v+s] = v
			}
		}
	}

	// if !ready {
	// 	getReady()
	// }

	for _, c := range replaceDict {
		str = c.Regex.ReplaceAllString(str, c.Char)
	}

	str = ignoreRegex.ReplaceAllString(str, "")

	str = strings.ToLower(str)

	formattedWords := make([]string, len(banned))
	pos := 0
	cacheID := ider.getID(words)
	reg, ok := cacher.getItem(cacheID)

	if !ok {
		for w, v := range banned {
			chars := make([]string, 0)
			for _, c := range w {
				chars = append(chars, string(c))
			}
			if words[v] <= 1 {
				formattedWords[pos] = fmt.Sprintf("(\\b(%s)\\b)", strings.Join(chars, "\\s*"))
			} else {
				formattedWords[pos] = fmt.Sprintf("(%s)", strings.Join(chars, "\\s*"))
			}
			pos++
		}

		reg, _ = regexp.Compile(strings.Join(formattedWords, "|"))

		cacher.setItem(cacheID, reg)

	}

	match := reg.FindString(str)
	// if match != "" {
	// 	return C.int(1)
	// } else {
	// 	return C.int(0)
	// }
	return match != ""
}

//export test
func test(rawStr *C.char, rawWords []*C.struct_word) {

	if !check(rawStr, rawWords) {

		d := color.New(color.Reset, color.ReverseVideo, color.FgGreen, color.Bold)
		d.Println(" CHECK PASSED ")
	} else {

		d := color.New(color.Reset, color.ReverseVideo, color.FgRed, color.Bold)
		d.Println(" CHECK FAILED ")
	}
}
