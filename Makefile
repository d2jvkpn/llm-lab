#!/usr/bin/make
SHELL := /bin/bash
config = "./configs/local.yaml"


check:
	. $$(yq .local.venv configs/local.yaml)/bin/activate && \
	flake8 --exclude=cache,data,configs,examples --select=F --ignore=E,W,C

lab:
	. $$(yq .local.venv configs/local.yaml)/bin/activate && \
	./lab.py --config=configs/local.yaml --host=127.0.0.1 --port=7871
