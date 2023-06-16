
.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-facebook-ads:${version}

build_docker_no_cache: 
	docker build . -t valmiio/destination-facebook-ads:${version} --no-cache

build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-facebook-ads:${version} \
		-t valmiio/destination-facebook-ads:stable \
		-t valmiio/destination-facebook-ads:latest \
		--no-cache --push .
