file := .version
version := $(shell cat ${file})
.PHONY: build_docker
build_docker: 
	docker build . -t valmiio/destination-google-ads:${version}
build_docker_no_cache: 
	docker build . -t valmiio/destination-google-ads:${version} --no-cache

