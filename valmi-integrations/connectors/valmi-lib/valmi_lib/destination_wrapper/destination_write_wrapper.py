from abc import abstractmethod
from collections import defaultdict, namedtuple
from datetime import datetime
from typing import Any, Dict, Iterable, Mapping
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteTraceMessage,
    AirbyteStateMessage,
    TraceType,
    AirbyteErrorTraceMessage,
)
from airbyte_cdk.models.airbyte_protocol import Type, AirbyteStateType

from valmi_lib.valmi_protocol import (
    ConfiguredValmiDestinationCatalog,
    ConfiguredValmiCatalog,
)
from valmi_lib.common.run_time_args import RunTimeArgs


class DestinationWriteWrapper:
    def __init__(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredValmiCatalog,
        configured_destination_catalog: ConfiguredValmiDestinationCatalog,
        state: Dict[str, Any],
    ):
        self.logger = logger
        self.config = config
        self.configured_catalog = configured_catalog
        self.configured_destination_catalog = configured_destination_catalog
        self.run_time_args = RunTimeArgs.parse_obj(config["run_time_args"] if "run_time_args" in config else {})

    @abstractmethod
    def initialise_message_handling(self):
        pass

    @abstractmethod
    def handle_message(self, msg, counter):
        pass

    @abstractmethod
    def finalise_message_handling(self):
        pass

    def start_message_handling(self, input_messages: Iterable[AirbyteMessage]):
        counter = 0
        counter_by_type = defaultdict(lambda: 0)
        chunk_id = 0
        run_time_args = RunTimeArgs.parse_obj(self.config["run_time_args"] if "run_time_args" in self.config else {})

        self.initialise_message_handling()
        for msg in input_messages:
            now = datetime.now()
            if msg.type == Type.RECORD:
                handler_response = namedtuple("MessageHandleData", ["flushed"])
                try:
                    handler_response = self.handle_message(msg, counter)
                except Exception as e:
                    yield AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            error=AirbyteErrorTraceMessage(message=str(e)),
                            emitted_at=int(datetime.now().timestamp()) * 1000,
                        ),
                    )
                    return

                counter = counter + 1
                sync_op = msg.record.data["_valmi_meta"]["_valmi_sync_op"]
                counter_by_type[sync_op] = counter_by_type[sync_op] + 1

                commit_state = False
                if handler_response.flushed:
                    commit_state = True

                if handler_response.flushed or counter % run_time_args.chunk_size == 0:
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=AirbyteStateMessage(
                            type=AirbyteStateType.STREAM,
                            data={
                                "records_delivered": counter_by_type,
                                "chunk_id": chunk_id,
                                "finished": False,
                                "commit_state": commit_state,
                                "commit_metric": True,
                            },
                        ),
                    )
                    if counter % run_time_args.chunk_size == 0:
                        counter_by_type.clear()
                        chunk_id = chunk_id + 1

                if (datetime.now() - now).seconds > 5:
                    self.logger.info("A log every 5 seconds - is this required??")

        self.finalise_message_handling()
        # Sync completed - final state message
        yield AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                data={
                    "records_delivered": counter_by_type,
                    "chunk_id": chunk_id,
                    "finished": True,
                    "commit_state": True,
                    "commit_metric": True,
                },
            ),
        )
