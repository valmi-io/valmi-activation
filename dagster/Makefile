
BUILDX = docker buildx

.PHONY: build_all

build-all: build_and_push_valmi_dagster build_and_push_valmi_repo

build-and-push-valmi-dagster:
	$(BUILDX) build --platform linux/amd64,linux/arm64 \
		-t valmiio/valmi-dagster:${valmi_dagster_version} \
		-t valmiio/valmi-dagster:stable \
		-t valmiio/valmi-dagster:latest \
		--no-cache --push -f Dockerfile.dagster .

build-and-push-valmi-repo:
	$(BUILDX) build --platform linux/amd64,linux/arm64 \
		-t valmiio/valmi-repo:${valmi_repo_version} \
		-t valmiio/valmi-repo:stable \
		-t valmiio/valmi-repo:latest \
		--no-cache --push -f Dockerfile.usercode .

