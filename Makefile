#!/usr/bin/make
SHELL := /bin/bash

check:
	flake8 --exclude=cache,data,configs,examples --select=F --ignore=E,W,C

run:
	./main.py --config=configs/local.yaml --host=127.0.0.1 --port=7871
