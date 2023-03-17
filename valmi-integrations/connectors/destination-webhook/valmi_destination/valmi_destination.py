import argparse
import io
import logging
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteMessage, Type
from valmi_protocol import ConfiguredValmiDestinationCatalog

logger = logging.getLogger("valmi")


class ValmiDestination(Destination):

    """
    def parse_args(self, args: List[str]) -> argparse.Namespace:
        parsed_args = None
        try:
            parsed_args = super().parse_args(args)
        except SystemExit:
            parent_parser = argparse.ArgumentParser(add_help=False)
            main_parser = argparse.ArgumentParser()
            subparsers = main_parser.add_subparsers(title="commands", dest="command")

            # discover
            discover_parser = subparsers.add_parser(
                "discover", help="outputs a catalog describing the source's schema", parents=[parent_parser]
            )
            required_discover_parser = discover_parser.add_argument_group("required named arguments")
            required_discover_parser.add_argument(
                "--config", type=str, required=True, help="path to the json configuration file"
            )
            parsed_args = main_parser.parse_args(args)
            return parsed_args

        return parsed_args
    """

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
        write_required = write_parser.add_argument_group("required named arguments")
        write_required.add_argument("--config", type=str, required=True, help="path to the JSON configuration file")
        write_required.add_argument(
            "--catalog", type=str, required=True, help="path to the configured catalog JSON file"
        )

        # discover
        discover_parser = subparsers.add_parser(
            "discover", help="outputs a catalog describing the source's schema", parents=[parent_parser]
        )
        required_discover_parser = discover_parser.add_argument_group("required named arguments")
        required_discover_parser.add_argument(
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
        if cmd == "discover":
            return self.discover_handler(parsed_args)
        else:
            return super().run_cmd(parsed_args)

    def discover_handler(self, parsed_args: argparse.Namespace) -> Iterable[AirbyteMessage]:
        config = self.read_config(config_path=parsed_args.config)
        catalog = self.discover(logger, config)
        yield AirbyteMessage(type=Type.CATALOG, catalog=catalog)

    def _run_write(
        self,
        config: Mapping[str, Any],
        configured_catalog_path: str,
        input_stream: io.TextIOWrapper,
    ) -> Iterable[AirbyteMessage]:
        catalog = ConfiguredValmiDestinationCatalog.parse_file(configured_catalog_path)
        input_messages = self._parse_input_stream(input_stream)
        logger.info("Begin writing to the destination...")
        yield from self.write(config=config, configured_catalog=catalog, input_messages=input_messages)
        logger.info("Writing complete.")
