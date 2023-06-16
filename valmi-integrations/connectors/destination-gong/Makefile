
.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-gong:${version} --build-arg VERSION=${version}

build_docker_no_cache:
	docker build . -t valmiio/destination-gong:${version} --build-arg VERSION=${version} --no-cache

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-gong:${version} \
		-t valmiio/destination-gong:stable \
		-t valmiio/destination-gong:latest \
		--no-cache --push .
