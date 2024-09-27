.EXPORT_ALL_VARIABLES:

POETRY_VERSION ?= 1.7.1

.PHONY: install-pip
install-pip:
	python -m pip install --upgrade pip

.PHONY: install-rye
install-rye:
	curl -sSf https://rye.astral.sh/get | bash

.PHONY: install-packages
install-packages:
	rye sync --no-lock

.PHONY: install
install: install-pip install-rye install-packages


.PHONY: test
test:
	rye test $(opts)


.PHONY: run
run:
	rye run edge-proxy-serve
