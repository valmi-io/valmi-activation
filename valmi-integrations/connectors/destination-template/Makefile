
.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-template:${version} --build-arg VERSION=${version}

build_docker_no_cache:
	docker build . -t valmiio/destination-template:${version} --build-arg VERSION=${version} --no-cache

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-template:${version} \
		-t valmiio/destination-template:stable \
		-t valmiio/destination-template:latest \
		--no-cache --push .
