#!/usr/bin/make
SHELL := /bin/bash

run:
	./main.py --config=configs/local.yaml --host=127.0.0.1 --port=7871
