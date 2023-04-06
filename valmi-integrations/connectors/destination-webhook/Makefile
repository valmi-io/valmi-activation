file := .version
version := $(shell cat ${file})
.PHONY: build_docker
build_docker: 
	docker build . -t valmiio/destination-webhook:${version} --build-arg VERSION=${version}

