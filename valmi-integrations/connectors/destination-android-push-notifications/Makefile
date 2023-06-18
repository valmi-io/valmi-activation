
BUILDX = docker buildx build
PLATFORMS = linux/amd64,linux/arm64
BUILDX_ARGS = --platform ${PLATFORMS} --allow security.insecure --no-cache --push

.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-android-push-notifications:${version}

build_docker_no_cache: 
	docker build . -t valmiio/destination-android-push-notifications:${version} --no-cache

build_and_push:
	$(BUILDX) $(BUILDX_ARGS) \
		-t valmiio/destination-android-push-notifications:${version} \
		-t valmiio/destination-android-push-notifications:stable \
		-t valmiio/destination-android-push-notifications:latest .
