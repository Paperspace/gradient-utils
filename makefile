SRC=$(shell pwd)
PIP=pip3
PYTHON=python
PYTEST_COV=pytest --cov=gradient-sdk
HELM:=helm
RELEASE_NAME=gradient-sdk
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
