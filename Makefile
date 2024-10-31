.PHONY: build run-server run-client

build:
	pdm install

run-server:
	python3 ./src/server.py 55111

run-client:
	python3 ./src/client.py 55111
