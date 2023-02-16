dc = docker-compose -f docker-compose.yml 
user_id:=$(shell id -u)
group_id:=$(shell id -g)

build:
	docker build . -t valmi/valmi-activation --build-arg USER_ID=$(user_id) --build-arg GROUP_ID=$(group_id)

run:
	$(dc) up -d valmi-activation

compile-requirements:
	$(dc) run --rm valmi-activation bash -c "\
		python -m pip install pip-tools && \
		pip-compile -U -o requirements/requirements.txt && \
		pip-compile -U requirements/test-requirements.in -o requirements/test-requirements.txt"

alembic-revision:
	$(dc) run --rm avalmi-activationpi alembic revision --autogenerate -m $(msg)

setup-db:
	$(dc) run --rm valmi-activation alembic upgrade head
