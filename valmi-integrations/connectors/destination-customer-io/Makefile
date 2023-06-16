
.PHONY: build_docker

build_docker: 
	docker build -t . valmiio/destination-customer-io:${version}

build_docker_no_cache: 
	docker build --no-cache . -t valmiio/destination-customer-io:${version}

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-customer-io:${version} \
		-t valmiio/destination-customer-io:stable \
		-t valmiio/destination-customer-io:latest \
		--no-cache --push .
