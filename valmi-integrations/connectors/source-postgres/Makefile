.PHONY: build_docker
build_docker: copy_dbt 
	docker build . -t valmiio/source-postgres:0.1.0

copy_dbt:
	rm -rf ./valmi_dbt/valmi_dbt_source_transform
	cp -r ../../valmi_dbt_source_transform ./valmi_dbt/valmi_dbt_source_transform
