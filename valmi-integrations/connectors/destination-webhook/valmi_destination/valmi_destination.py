import argparse
import io
import logging
import sys
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteMessage, Type
from valmi_protocol import ConfiguredValmiDestinationCatalog
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

logger = logging.getLogger("airbyte")


class ValmiDestination(Destination):
    '''
    def read_state(self, state_path: str) -> Union[List[AirbyteStateMessage], MutableMapping[str, Any]]:
        """
        Retrieves the input state of a sync by reading from the specified JSON file. Incoming state can be deserialized  as a list of AirbyteStateMessages for the per-stream state format. Regardless of the
        incoming input type, it will always be transformed and output as a list of AirbyteStateMessage(s).
        :param state_path: The filepath to where the stream states are located
        :return: The complete stream state based on the connector's previous sync
        """
        if state_path:
            state_obj = self._read_json_file(state_path)
            is_per_stream_state = isinstance(state_obj, List)
            if is_per_stream_state:
                parsed_state_messages = []
                for state in state_obj:
                    parsed_message = AirbyteStateMessage.parse_obj(state)
                    if not parsed_message.stream and not parsed_message.data and not parsed_message.global_:
                        raise ValueError("AirbyteStateMessage should contain either a stream, global, or state field")
                    parsed_state_messages.append(parsed_message)
                return parsed_state_messages
        return None
    '''

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

        # if cmd not in ["discover", "write"]:
        if cmd not in ["discover"]:
            for msg in super().run_cmd(parsed_args):
                yield msg
            return

        spec = self.spec(logger)
        config = self.read_config(config_path=parsed_args.config)

        if self.check_config_against_spec:
            try:
                check_config_against_spec_or_exit(config, spec)
            except AirbyteTracedException as traced_exc:
                raise traced_exc

        if cmd == "discover":
            for msg in self.discover_handler(config, parsed_args):
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
                input_stream=wrapped_stdin,
            )
            return

    def discover_handler(self, config, parsed_args: argparse.Namespace) -> Iterable[AirbyteMessage]:
        catalog = self.discover(logger, config)
        yield AirbyteMessage(type=Type.CATALOG, catalog=catalog)

    def _run_write(
        self,
        config: Mapping[str, Any],
        configured_catalog_path: str,
        input_stream: io.TextIOWrapper,
        # state: Dict[str, any],
    ) -> Iterable[AirbyteMessage]:
        catalog = ConfiguredValmiDestinationCatalog.parse_file(configured_catalog_path)
        input_messages = self._parse_input_stream(input_stream)
        logger.info("Begin writing to the destination...")
        yield from self.write(
            # config=config, configured_catalog=catalog, input_messages=input_messages, state=state, logger=logger
            config=config,
            configured_catalog=catalog,
            input_messages=input_messages,
            logger=logger,
        )
        logger.info("Writing complete.")
