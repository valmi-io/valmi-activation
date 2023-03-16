from jinja2 import Environment, FileSystemLoader

from fal import FalDbt
import dbt.adapters.factory as adapters_factory
import os
from dbt.adapters.sql import SQLAdapter
from dbt.adapters.base.relation import BaseRelation
from airbyte_cdk.logger import AirbyteLogger
from faldbt import lib, parse

from dbt.events.functions import cleanup_event_logger

from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
)


class CustomFalDbt(FalDbt):
    def __init__(self, *args, **kwargs) -> None:
        if "basic" not in kwargs:
            super(CustomFalDbt, self).__init__(*args, **kwargs)
        else:
            self.project_dir = os.path.realpath(os.path.expanduser(kwargs["project_dir"]))
            self.profiles_dir = os.path.realpath(os.path.expanduser(kwargs["profiles_dir"]))

            lib.initialize_dbt_flags(profiles_dir=self.profiles_dir)

            self._config = parse.get_dbt_config(
                project_dir=self.project_dir,
                profiles_dir=self.profiles_dir,
            )

            lib.register_adapters(self._config)
            cleanup_event_logger()


class DbtAirbyteAdpater:
    def get_jinja_template(self, logger: AirbyteLogger, template_fname):
        file_loader = FileSystemLoader(self.get_cur_dir())
        env = Environment(loader=file_loader)
        template = env.get_template(template_fname)
        return template

    def get_cur_dir(self):
        return os.path.dirname(os.path.abspath(__file__))

    def get_abs_path(self, path):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

    def write_profiles_config_from_spec(self, logger: AirbyteLogger, config, filename):
        template = self.get_jinja_template(logger, "profiles_template.jinja")
        output = template.render(config=config)
        with open(self.get_abs_path(filename), "w") as f:
            f.write(output)

    def check_connection(self):
        faldbt = CustomFalDbt(
            basic=True, profiles_dir=self.get_cur_dir(), project_dir=self.get_abs_path("valmi_dbt_source_transform")
        )
        adapter: SQLAdapter = adapters_factory.get_adapter(faldbt._config)
        adapter.connections.open(adapter.acquire_connection("check_connection"))

    def discover_streams(self, logger: AirbyteLogger, config):
        self.faldbt = CustomFalDbt(
            basic=True, profiles_dir=self.get_cur_dir(), project_dir=self.get_abs_path("valmi_dbt_source_transform")
        )
        self.adapter: SQLAdapter = adapters_factory.get_adapter(self.faldbt._config)

        with self.adapter.connection_named("discover-connection"):
            if "namespace" in config:
                return (
                    False,
                    self.adapter.list_relations(self.faldbt._config.credentials.database, schema=config["namespace"]),
                )
            else:
                return (True, self.adapter.list_schemas(self.faldbt._config.credentials.database))

    def get_columns(self, adapter: SQLAdapter, relation: BaseRelation):
        with self.adapter.connection_named("getcolumns-connection"):
            return adapter.get_columns_in_relation(relation)

    def generate_project_yml(self, logger: AirbyteLogger, catalog: ConfiguredAirbyteCatalog, sync_id, filename):
        template = self.get_jinja_template("dbt_project.jinja")

        if catalog.streams[0].sync_mode == "full_refresh":
            full_refresh = "true"

        # override full_refresh from run_time_args
        if hasattr(catalog, "run_time_args") and "full_refresh" in catalog.run_time_args:
            full_refresh = catalog.run_time_args["full_refresh"]

        col_arr_str = ",".join([f'"{col}"' for col in catalog.streams[0].stream.json_schema["properties"].keys()])
        args = {
            "sync_id": sync_id,
            "full_refresh": full_refresh,
            "columns": f"[{col_arr_str}]",
            "id_key": catalog.streams[0].id_key,
            "name": catalog.streams[0].stream.name,
        }

        output = template.render(args=args)
        with open(self.get_abs_path(filename), "w") as f:
            f.write(output)

    def generate_source_yml(self, logger: AirbyteLogger, config, catalog, filename):
        template = self.get_jinja_template("source_schema.jinja")

        source = {
            "stream": catalog["streams"][0]["stream"]["name"],
            "schema": config["namespace"],
            "database": config["database"],
        }

        output = template.render(source=source)
        with open(self.get_abs_path(filename), "w") as f:
            f.write(output)

    def execute_sql(faldbt, sql: str):
        compiled_result = lib.compile_sql(
            faldbt.project_dir,
            faldbt.profiles_dir,
            faldbt._profile_target,
            sql,
            config=faldbt._config,
        )
        # NOTE: changed in version 1.3.0 to `compiled_code`
        if hasattr(compiled_result, "compiled_code"):
            sql = compiled_result.compiled_code
        else:
            sql = compiled_result.compiled_sql

        adapter: SQLAdapter = adapters_factory.get_adapter(faldbt._config)  # type: ignore
        with adapter.connection_named("faldbt"):
            return adapter.execute(sql, fetch=True)
