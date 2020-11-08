#!/bin/bash

export GOTRACEBACK=all
GOTSIG=no
handle_kill() {
  GOTSIG=yes
  echo killin
  kill `cat /tmp/pid1`
  wait_for_lock_deletion
  exit
}

wait_for_lock_deletion() {
  if [ -f /tmp/asb.lock ]; then
    inotifywait -e delete /tmp/asb.lock >/dev/null 2>&1
  fi
}

trap handle_kill SIGINT SIGTERM

wait_for_kill() {
  while [ GOTSIG != yes ]; do
    sleep 0.1
  done
}

event_stuff() {
  while true; do
    make run &
    echo $! > /tmp/pid1
    inotifywait -e modify,move,create,delete,attrib -r $(find -name '*.go') >/dev/null 2>&1
    kill `cat /tmp/pid1`
    wait_for_lock_deletion
  done
}

event_stuff &
wait_for_kill &
wait $!
