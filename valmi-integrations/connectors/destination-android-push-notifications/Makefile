file := .version
version := $(shell cat ${file})
.PHONY: build_docker
build_docker: 
	docker build . -t valmiio/destination-android-push-notifications:${version}

build_docker_no_cache: 
	docker build . -t valmiio/destination-android-push-notifications:${version} --no-cache
