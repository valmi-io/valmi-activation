"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, March 8th 2023, 11:38:42 am
Author: Rajashekar Varkala @ valmi.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import io
import logging
import sys
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteMessage, Type, AirbyteConnectionStatus, Status
from abc import abstractmethod
from valmi_connector_lib.valmi_protocol import ConfiguredValmiDestinationCatalog, ConfiguredValmiCatalog
from airbyte_cdk import AirbyteLogger

logger = logging.getLogger("airbyte")


class ValmiDestination(Destination):
    def parse_args(self, args: List[str]) -> argparse.Namespace:
        parent_parser = argparse.ArgumentParser(add_help=False)
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(title="commands", dest="command")

        # spec
        subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

        # check
        check_parser = subparsers.add_parser(
            "check", help="checks the config can be used to connect", parents=[parent_parser]
        )
        required_check_parser = check_parser.add_argument_group("required named arguments")
        required_check_parser.add_argument(
            "--config", type=str, required=True, help="path to the json configuration file"
        )

        # write
        write_parser = subparsers.add_parser("write", help="Writes data to the destination", parents=[parent_parser])
        # write_parser.add_argument("--state", type=str, required=False, help="path to the json-encoded state file")
        write_required = write_parser.add_argument_group("required named arguments")
        write_required.add_argument("--config", type=str, required=True, help="path to the JSON configuration file")
        write_required.add_argument(
            "--catalog", type=str, required=True, help="path to the configured catalog JSON file"
        )
        write_required.add_argument(
            "--destination_catalog",
            type=str,
            required=True,
            help="path to the configured destination catalog JSON file",
        )

        # discover
        discover_parser = subparsers.add_parser(
            "discover", help="outputs a catalog describing the source's schema", parents=[parent_parser]
        )
        required_discover_parser = discover_parser.add_argument_group("required named arguments")
        required_discover_parser.add_argument(
            "--config", type=str, required=True, help="path to the json configuration file"
        )

        # create object
        create_parser = subparsers.add_parser(
            "create", help="create an object on the destination", parents=[parent_parser]
        )
        required_create_parser = create_parser.add_argument_group("required named arguments")
        required_create_parser.add_argument("--object", type=str, required=True, help="path to the json object file")
        required_create_parser.add_argument(
            "--config", type=str, required=True, help="path to the json configuration file"
        )

        parsed_args = main_parser.parse_args(args)
        cmd = parsed_args.command
        if not cmd:
            raise Exception("No command entered. ")
        elif cmd not in Destination.VALID_CMDS:
            # This is technically dead code since parse_args() would fail if this was the case
            # But it's non-obvious enough to warrant placing it here anyways
            raise Exception(f"Unknown command entered: {cmd}")

        return parsed_args

    def run_cmd(self, parsed_args: argparse.Namespace) -> Iterable[AirbyteMessage]:
        cmd = parsed_args.command

        # if cmd not in ["discover", "write"]:
        if cmd not in ["discover", "write"]:
            for msg in super().run_cmd(parsed_args):
                yield msg
            return

        config = self.read_config(config_path=parsed_args.config)

        if cmd == "discover":
            for msg in self.discover_handler(config, parsed_args):
                yield msg
            return

        if cmd == "create":
            for msg in self.create_handler(config, parsed_args):
                yield msg
            return

        elif cmd == "write":
            # state = self.read_state(parsed_args.state)

            # Wrap in UTF-8 to override any other input encodings
            wrapped_stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
            yield from self._run_write(
                # config=config, configured_catalog_path=parsed_args.catalog, input_stream=wrapped_stdin, state=state
                config=config,
                configured_catalog_path=parsed_args.catalog,
                configured_destination_catalog_path=parsed_args.destination_catalog,
                input_stream=wrapped_stdin,
            )
            return

    def create_handler(self, config, parsed_args: argparse.Namespace) -> Iterable[AirbyteMessage]:
        try:
            object_schema = self.read_config(config_path=parsed_args.object)

            self.create(logger, config, object_schema)
            yield AirbyteMessage(
                type=Type.CONNECTION_STATUS, connectionStatus=AirbyteConnectionStatus(status=Status.SUCCEEDED)
            )
        except Exception as err:
            yield AirbyteMessage(
                type=Type.CONNECTION_STATUS,
                connectionStatus=AirbyteConnectionStatus(status=Status.Failed, message=str(err)),
            )

    def discover_handler(self, config, parsed_args: argparse.Namespace) -> Iterable[AirbyteMessage]:
        catalog = self.discover(logger, config)
        yield AirbyteMessage(type=Type.CATALOG, catalog=catalog)

    @abstractmethod
    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredValmiCatalog,
        input_messages: Iterable[AirbyteMessage],
        configured_destination_catalog: ConfiguredValmiDestinationCatalog,
        logger: AirbyteLogger,
    ) -> Iterable[AirbyteMessage]:
        """Implement to define how the connector writes data to the destination"""

    def _run_write(
        self,
        config: Mapping[str, Any],
        configured_catalog_path: str,
        configured_destination_catalog_path: str,
        input_stream: io.TextIOWrapper,
        # state: Dict[str, any],
    ) -> Iterable[AirbyteMessage]:
        catalog = ConfiguredValmiCatalog.parse_file(configured_catalog_path)
        destination_catalog = ConfiguredValmiDestinationCatalog.parse_file(configured_destination_catalog_path)
        input_messages = self._parse_input_stream(input_stream)
        logger.info("Begin writing to the destination...")
        yield from self.write(
            # config=config, configured_catalog=catalog, input_messages=input_messages, state=state, logger=logger
            config=config,
            configured_catalog=catalog,
            configured_destination_catalog=destination_catalog,
            input_messages=input_messages,
            logger=logger,
        )
        logger.info("Writing complete.")
