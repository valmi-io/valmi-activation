
dagster_version_file := .version_dagster

# Check if the 'VALMI_DAGSTER_VERSION' environment variable is set.
ifeq ($(VALMI_DAGSTER_VERSION),)
    $(info The 'VALMI_DAGSTER_VERSION' environment variable is not set. Reading it from '$(dagster_version_file)')
    dagster_version := $(shell cat $(dagster_version_file))
else
		dagster_version := $(VALMI_DAGSTER_VERSION)
endif

valmi_repo_version_file := .version_valmi_repo
# Check if the 'VALMI_REPO_VERSION' environment variable is set.
ifeq ($(VALMI_REPO_VERSION),)
    $(info The 'VALMI_REPO_VERSION' environment variable is not set. Reading it from '$(valmi_repo_version_file)')
    valmi_repo_version := $(shell cat $(valmi_repo_version_file))
else
		valmi_repo_version := $(VALMI_REPO_VERSION)
endif

BUILDX = docker buildx

.PHONY: build_all

build-all: build_and_push_valmi_dagster build_and_push_valmi_repo

build-and-push-valmi-dagster:
	$(BUILDX) build --platform linux/amd64,linux/arm64 \
		-t valmiio/valmi-dagster:${dagster_version} \
		-t valmiio/valmi-dagster:stable \
		-t valmiio/valmi-dagster:latest \
		--no-cache --push -f Dockerfile.dagster .

build-and-push-valmi-repo:
	$(BUILDX) build --platform linux/amd64,linux/arm64 \
		-t valmiio/valmi-repo:${valmi_repo_version} \
		-t valmiio/valmi-repo:stable \
		-t valmiio/valmi-repo:latest \
		--no-cache --push -f Dockerfile.usercode .

