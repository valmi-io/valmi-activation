file := .version
version := $(shell cat ${file})
.PHONY: build_docker
build_docker: 
	docker build . -t valmiio/destination-facebook-ads:${version}

build_docker_no_cache: 
	docker build . -t valmiio/destination-facebook-ads:${version} --no-cache
