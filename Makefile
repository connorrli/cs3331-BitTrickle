.PHONY: build run-server run-client

build:
	pdm install

run-server:
	python3 ./src/server.py 55222

run-client:
	python3 ./src/client.py 55222
