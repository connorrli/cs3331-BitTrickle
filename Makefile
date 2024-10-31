.PHONY: build run-server run-client

build:
	pdm install

run-server:
	python3 ./src/server/server.py

run-client:
	python3 ./src/client/client.py