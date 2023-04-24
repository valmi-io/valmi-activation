file := .version
version := $(shell cat ${file})
.PHONY: build_docker
build_docker: 
	docker build . -t valmiio/destination-hubspot:${version}

