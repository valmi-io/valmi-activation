
DOCKER = docker
BUILDX = $(DOCKER) buildx
PLATFORMS = linux/amd64,linux/arm64
BUILDX_ARGS = --platform ${PLATFORMS} --allow security.insecure --no-cache --push

.PHONY: build_all

build-all: build_and_push_valmi_dagster build_and_push_valmi_repo

build-and-push-valmi-dagster:
	$(BUILDX) build $(BUILDX_ARGS) \
		-t valmiio/valmi-dagster:${valmi_dagster_version} \
		-t valmiio/valmi-dagster:stable \
		-t valmiio/valmi-dagster:latest \
		-f Dockerfile.dagster .

build-and-push-valmi-repo:
	$(BUILDX) build $(BUILDX_ARGS) \
		-t valmiio/valmi-repo:${valmi_repo_version} \
		-t valmiio/valmi-repo:stable \
		-t valmiio/valmi-repo:latest \
		-f Dockerfile.usercode .

