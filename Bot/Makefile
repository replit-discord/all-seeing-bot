#!make

include .env
export $(shell sed 's/=.*//' .env)

run:
	python3 main.py # > logs.txt

shell:
	python3 shell.py