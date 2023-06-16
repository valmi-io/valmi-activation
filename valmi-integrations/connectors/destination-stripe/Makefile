
.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-stripe:${version}

build_docker_no_cache: 
	docker build --no-cache . -t valmiio/destination-stripe:${version}

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-stripe:${version} \
		-t valmiio/destination-stripe:stable \
		-t valmiio/destination-stripe:latest \
		--no-cache --push .
