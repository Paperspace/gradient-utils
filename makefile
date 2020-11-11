SRC=$(shell pwd)
PIP=pip3
RELEASE_NAME=gradient_utils
PWD=$(shell pwd)

export PYTHONPATH:=$(SRC)

pip-update:
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade setuptools

pip-install: pip-update
	$(PIP) install --upgrade .

pip-install-dev: pip-update
	$(PIP) install --upgrade -e .[dev]

pip-install-publish: pip-update
	$(PIP) install twine

run-tests:
	tox

clean-build:
	rm -rf build dist

build: clean-build
	python setup.py sdist bdist_wheel

local-publish-test: pip-install-publish build
	twine upload -r test dist/*

local-publish: pip-install-publish build
	twine upload -r pypi dist/*

publish: pip-install-publish build
	twine upload dist/*

dc-setup:
	docker-compose -f docker-compose.ci.yml up --remove-orphans -d pushgateway
	docker-compose -f docker-compose.ci.yml build utils

dc-test:
	docker-compose -f docker-compose.ci.yml run -t utils poetry run pytest
