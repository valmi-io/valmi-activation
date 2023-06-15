dc = docker-compose -f docker-compose.yml 
user_id:=$(shell id -u)
group_id:=$(shell id -g)

DOCKER = docker
BUILDX = $(DOCKER) buildx
BUILDER_NAME=valmi-docker-builder

ECHO = echo

# Get all the connectors sub direcotries
CONNECTORS := $(shell find valmi-integrations/connectors -maxdepth 1 -type d -not -path .)

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
	$(dc) run --rm valmi-activation bash -c "cd src &&  alembic revision --autogenerate -m $(msg)"

setup-db:
	$(dc) run --rm valmi-activation bash -c "cd src && alembic upgrade head"

setup-buildx:
	$(DOCKER) run --privileged --rm tonistiigi/binfmt --install all
	$(BUILDX) rm $(BUILDER_NAME) || true
	$(BUILDX) create --name $(BUILDER_NAME) --driver docker-container --bootstrap
	$(BUILDX) use $(BUILDER_NAME)

build-connector:
	$(MAKE) -C valmi-integrations/connectors/$(CONNECTOR_NAME) build_docker

build-and-push-connector:
	$(MAKE) -C valmi-integrations/connectors/$(CONNECTOR_NAME) build_and_push

build-connectors-all:
	@for dir in $(CONNECTORS); do \
		if [ -f $$dir/Makefile ]; then \
			$(MAKE) -C $$dir build_docker; \
		fi \
	done

build-and-push-connectors-all:
	@for dir in $(CONNECTORS); do \
		if [ -f $$dir/Makefile ]; then \
			$(MAKE) -C $$dir build_and_push; \
		fi \
	done

build-and-push-valmi-dagster:
	$(MAKE) -C dagster build-and-push-valmi-dagster

build-and-push-valmi-repo:
	$(MAKE) -C dagster build-and-push-valmi-repo

version_file := .version

# Check if the 'VALMI_ACTIVATION_VERSION' environment variable is set.
ifeq ($(VALMI_ACTIVATION_VERSION),)
    $(info The 'VALMI_ACTIVATION_VERSION' environment variable is not set. Reading it from '$(version_file)')
    valmi_activation_version := $(shell cat $(version_file))
else
		valmi_activation_version := $(VALMI_ACTIVATION_VERSION)
endif

build-and-push-valmi-activation:
	$(BUILDX) build --platform linux/amd64,linux/arm64 \
		--cache-from valmiio/valmi-activation:latest \
		-t valmiio/valmi-activation:${valmi_activation_version} \
		-t valmiio/valmi-activation:stable \
		-t valmiio/valmi-activation:latest \
		--push -f Dockerfile.prod .
