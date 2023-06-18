
BUILDX = docker buildx build
PLATFORMS = linux/amd64,linux/arm64
BUILDX_ARGS = --platform ${PLATFORMS} --allow security.insecure --no-cache --push

.PHONY: build_docker

build_docker: copy_dbt 
	docker build . -t valmiio/source-postgres:${version} --build-arg VERSION=${version}

build_docker_no_cache: copy_dbt 
	docker build . -t valmiio/source-postgres:${version} --build-arg VERSION=${version} --no-cache

copy_dbt:
	rm -rf ./valmi_dbt/valmi_dbt_source_transform
	cp -r ../../valmi_dbt_source_transform ./valmi_dbt/valmi_dbt_source_transform

build_and_push: copy_dbt
	$(BUILDX) $(BUILDX_ARGS) \
		-t valmiio/source-postgres:${version} \
		-t valmiio/source-postgres:stable \
		-t valmiio/source-postgres:latest .