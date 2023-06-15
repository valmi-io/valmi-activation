version_file := .version

# Check if the 'CONNECTOR_VERSION' environment variable is set.
ifeq ($(CONNECTOR_VERSION),)
    $(info The 'CONNECTOR_VERSION' environment variable is not set. Reading it from '$(version_file)')
    version := $(shell cat $(version_file))
else
		version := $(CONNECTOR_VERSION)
endif

.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-android-push-notifications:${version}

build_docker_no_cache: 
	docker build . -t valmiio/destination-android-push-notifications:${version} --no-cache

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-android-push-notifications:${version} \
		-t valmiio/destination-android-push-notifications:stable \
		-t valmiio/destination-android-push-notifications:latest \
		--no-cache --push .
