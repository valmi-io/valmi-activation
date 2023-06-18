
BUILDX = docker buildx build
PLATFORMS = linux/amd64,linux/arm64
BUILDX_ARGS = --platform ${PLATFORMS} --allow security.insecure --no-cache --push

.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-facebook-ads:${version}

build_docker_no_cache: 
	docker build . -t valmiio/destination-facebook-ads:${version} --no-cache

build_and_push:
	$(BUILDX) $(BUILDX_ARGS) \
		-t valmiio/destination-facebook-ads:${version} \
		-t valmiio/destination-facebook-ads:stable \
		-t valmiio/destination-facebook-ads:latest .
