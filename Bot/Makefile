#!make

include .env
export $(shell sed 's/=.*//' .env)

run:
	python3 main.py 2>&1 | tee logs.txt 

shell:
	python3 shell.py