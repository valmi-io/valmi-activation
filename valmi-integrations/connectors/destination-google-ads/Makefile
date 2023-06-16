
.PHONY: build_docker

build_docker: 
	docker build . -t valmiio/destination-google-ads:${version}

build_docker_no_cache: 
	docker build . -t valmiio/destination-google-ads:${version} --no-cache


build_and_push:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t valmiio/destination-google-ads:${version} \
		-t valmiio/destination-google-ads:stable \
		-t valmiio/destination-google-ads:latest \
		--no-cache --push .
