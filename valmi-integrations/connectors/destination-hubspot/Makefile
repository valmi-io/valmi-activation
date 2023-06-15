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
	docker build . -t valmiio/destination-hubspot:${version}

build_docker_no_cache: 
	docker build --no-cache . -t valmiio/destination-hubspot:${version}

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-hubspot:${version} \
		-t valmiio/destination-hubspot:stable \
		-t valmiio/destination-hubspot:latest \
		--no-cache --push .
