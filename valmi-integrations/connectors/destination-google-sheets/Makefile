
.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-google-sheets:${version}

build_docker_no_cache: 
	docker build --no-cache . -t valmiio/destination-google-sheets:${version}

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-google-sheets:${version} \
		-t valmiio/destination-google-sheets:stable \
		-t valmiio/destination-google-sheets:latest \
		--no-cache --push .
