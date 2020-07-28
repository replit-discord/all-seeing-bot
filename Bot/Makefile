#!make

include .env
export $(shell sed 's/=.*//' .env)

run:
	python3.8 main.py | tee logs.txt 

shell:
	python3 shell.py