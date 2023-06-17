
BUILDX = docker buildx build
PLATFORMS = linux/amd64,linux/arm64
BUILDX_ARGS = --platform ${PLATFORMS} --allow security.insecure --no-cache --push

.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-google-sheets:${version}

build_docker_no_cache: 
	docker build --no-cache . -t valmiio/destination-google-sheets:${version}

build_and_push:
	$(BUILDX) $(BUILDX_ARGS) \
		-t valmiio/destination-google-sheets:${version} \
		-t valmiio/destination-google-sheets:stable \
		-t valmiio/destination-google-sheets:latest .
