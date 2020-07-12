#!make

include .env
export $(shell sed 's/=.*//' .env)

run:
	python3 main.py > logs.txt 2>&1

shell:
	python3 shell.py