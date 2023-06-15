version_file := .version

# Check if the 'CONNECTOR_VERSION' environment variable is set.
ifeq ($(CONNECTOR_VERSION),)
    $(info The 'CONNECTOR_VERSION' environment variable is not set. Reading it from '$(version_file)')
    version := $(shell cat $(version_file))
else
		version := $(CONNECTOR_VERSION)
endif

.PHONY: build_docker

build_docker: copy_dbt 
	docker build . -t valmiio/source-redshift:${version} --build-arg VERSION=${version}

build_docker_no_cache: copy_dbt 
	docker build . -t valmiio/source-redshift:${version} --build-arg VERSION=${version} --no-cache

copy_dbt:
	rm -rf ./valmi_dbt/valmi_dbt_source_transform
	cp -r ../../valmi_dbt_source_transform ./valmi_dbt/valmi_dbt_source_transform

build_and_push: copy_dbt
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/source-redshift:${version} \
		-t valmiio/source-redshift:stable \
		-t valmiio/source-redshift:latest \
		--no-cache --push .
