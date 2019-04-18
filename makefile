SRC=$(shell pwd)
PIP=pip3
RELEASE_NAME=gradient_sdk
PWD=$(shell pwd)

export PYTHONPATH:=$(SRC)

pip-update:
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade setuptools

pip-install: pip-update
	$(PIP) install --upgrade .

pip-install-dev: pip-update
	$(PIP) install --upgrade -e .[dev]

run-tests:
	tox
