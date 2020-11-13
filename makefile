SRC=$(shell pwd)
PIP=pip3
RELEASE_NAME=gradient_utils
PWD=$(shell pwd)

export PYTHONPATH:=$(SRC)

clean-build-publish:
	rm -rf dist
	docker-compose -f docker-compose.ci.yml build utils
	docker-compose -f docker-compose.ci.yml run -e POETRY_PYPI_TOKEN_PYPI utils poetry build && poetry publish

dc-setup:
	docker-compose -f docker-compose.ci.yml up --remove-orphans -d pushgateway
	docker-compose -f docker-compose.ci.yml build utils

dc-test:
	docker-compose -f docker-compose.ci.yml run utils poetry run pytest
