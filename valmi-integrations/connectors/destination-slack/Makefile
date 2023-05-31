file := .version
version := $(shell cat ${file})
.PHONY: build_docker
build_docker: 
	docker build . -t valmiio/destination-slack:${version}

build_docker_no_cache: 
	docker build --no-cache . -t valmiio/destination-slack:${version}
