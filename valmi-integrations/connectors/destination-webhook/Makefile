
.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-webhook:${version} --build-arg VERSION=${version}

build_docker_no_cache:
	docker build . -t valmiio/destination-webhook:${version} --build-arg VERSION=${version} --no-cache

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-webhook:${version} \
		-t valmiio/destination-webhook:stable \
		-t valmiio/destination-webhook:latest \
		--no-cache --push .
