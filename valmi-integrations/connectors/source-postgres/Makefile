file := .version
version := $(shell cat ${file})
.PHONY: build_docker
build_docker: copy_dbt 
	docker build . -t valmiio/source-postgres:${version} --build-arg VERSION=${version}

build_docker_no_cache: copy_dbt 
	docker build . -t valmiio/source-postgres:${version} --build-arg VERSION=${version} --no-cache

copy_dbt:
	rm -rf ./valmi_dbt/valmi_dbt_source_transform
	cp -r ../../valmi_dbt_source_transform ./valmi_dbt/valmi_dbt_source_transform
