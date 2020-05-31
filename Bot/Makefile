#!make

include .env
export $(shell sed 's/=.*//' .env)

run:
	python3 main.py

shell:
	python3 shell.py