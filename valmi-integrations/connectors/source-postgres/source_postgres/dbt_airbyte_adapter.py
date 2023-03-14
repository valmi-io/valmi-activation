from jinja2 import Environment, FileSystemLoader

from fal import FalDbt
import dbt.adapters.factory as adapters_factory
import os
from dbt.adapters.sql import SQLAdapter
from dbt.adapters.base.relation import BaseRelation
from airbyte_cdk.logger import AirbyteLogger
from faldbt import lib, parse

from dbt.events.functions import cleanup_event_logger


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
    def write_profiles_config_from_spec(self, logger: AirbyteLogger, config, filename):
        CUR_DIR = os.path.dirname(os.path.abspath(__file__))
        logger.debug(CUR_DIR)
        file_loader = FileSystemLoader(CUR_DIR)
        env = Environment(loader=file_loader)
        template = env.get_template("profiles-template.jinja")
        output = template.render(config=config)
        with open(os.path.join(CUR_DIR, filename), "w") as f:
            f.write(output)

    def check_connection(self):
        CUR_DIR = os.path.dirname(os.path.abspath(__file__))

        faldbt = CustomFalDbt(basic=True, profiles_dir=CUR_DIR, project_dir=os.path.join(CUR_DIR, "dbt_project"))
        adapter: SQLAdapter = adapters_factory.get_adapter(faldbt._config)
        adapter.connections.open(adapter.acquire_connection("check_connection"))

    def discover_streams(self, logger: AirbyteLogger, config):
        CUR_DIR = os.path.dirname(os.path.abspath(__file__))

        self.faldbt = CustomFalDbt(basic=True, profiles_dir=CUR_DIR, project_dir=os.path.join(CUR_DIR, "dbt_project"))
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
