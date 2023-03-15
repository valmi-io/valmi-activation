.PHONY: build_docker
build_docker: copy_dbt 
	docker build . -t valmiio/source-postgres:dev

copy_dbt:
	cp -r ../../valmi_dbt_source_transform ./valmi_dbt/valmi_dbt_source_transform
