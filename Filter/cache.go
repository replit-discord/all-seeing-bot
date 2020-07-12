package main

import (
	"fmt"
	"regexp"
	"strconv"
	"time"
)

type cachedItem struct {
	expiration time.Time
	value      *regexp.Regexp
}

var cacher objCacher

type objCacher struct {
	items map[string]*cachedItem
}

func (c *objCacher) checkExpirey() {
	delKeys := make([]string, 0)
	for k, v := range c.items {
		if time.Now().After(v.expiration) {
			delKeys = append(delKeys, k)
		}
	}

	for _, v := range delKeys {
		delete(c.items, v)
	}
}

func (c *objCacher) setItem(key string, reg *regexp.Regexp) {
	c.items[key] = &cachedItem{
		value:      reg,
		expiration: time.Now().Add(time.Minute * 30),
	}
}

func (c *objCacher) getItem(key string) (*regexp.Regexp, bool) {
	i, ok := c.items[key]
	if !ok {
		return nil, false
	}

	// Reset the expiration
	i.expiration = time.Now().Add(time.Minute * 30)
	fmt.Println(i)
	return i.value, true
}

func (c *objCacher) daemon() {
	t := time.NewTicker(time.Second)

	for {
		select {
		case <-t.C:
			c.checkExpirey()
		}
	}
}

type listIDer struct {
	data   map[string]map[string]uint8
	nextID int
}

func (l *listIDer) getID(banned map[string]uint8) string {
	for i, v := range l.data {
		bad := false
		for w, p := range v {
			d, ok := banned[w]
			if !ok || d != p {
				bad = true
				break
			}
		}

		if !bad {
			return i
		}
	}

	id := strconv.Itoa(l.nextID)
	l.nextID++

	l.data[id] = banned

	return id
}

var ider listIDer

func init() {
	cacher = objCacher{items: make(map[string]*cachedItem)}
	ider = listIDer{data: make(map[string]map[string]uint8)}

	go cacher.daemon()
}
