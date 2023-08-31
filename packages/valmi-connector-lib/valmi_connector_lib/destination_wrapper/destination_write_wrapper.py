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

from valmi_connector_lib.valmi_protocol import (
    ConfiguredValmiDestinationCatalog,
    ConfiguredValmiCatalog
)
from valmi_connector_lib.common.run_time_args import RunTimeArgs

HandlerResponseData = namedtuple(
    "HandlerResponseData", ["flushed", "metrics", "emittable_records"], defaults=(False, {}, [])
)


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
        self.previous_state = state

    @abstractmethod
    def initialise_message_handling(self) -> None:
        pass

    @abstractmethod
    def handle_message(self, msg: AirbyteMessage, counter: int) -> HandlerResponseData:
        pass

    @abstractmethod
    def finalise_message_handling(self) -> HandlerResponseData:
        pass

    def read_chunk_id_checkpoint(self):
        if self.previous_state is not None \
                and 'state' in self.previous_state \
                and 'data' in self.previous_state['state'] \
                and 'chunk_id' in self.previous_state['state']['data']:
            return self.previous_state['state']['data']['chunk_id'] + 1
        return 1

    def start_message_handling(self, input_messages: Iterable[AirbyteMessage]) -> AirbyteMessage:
        counter: int = 0
        counter_by_type: dict[str, int] = defaultdict(lambda: 0)
        chunk_id = self.read_chunk_id_checkpoint()
        run_time_args = RunTimeArgs.parse_obj(self.config["run_time_args"] if "run_time_args" in self.config else {})

        self.initialise_message_handling()
        for msg in input_messages:
            now = datetime.now()
            if msg.type == Type.RECORD:
                counter = counter + 1

                handler_response = HandlerResponseData()
                try:
                    handler_response = self.handle_message(msg, counter)
                    if handler_response.emittable_records:
                        for record in handler_response.emittable_records:
                            yield AirbyteMessage(
                                type=Type.RECORD,
                                record=record,
                            )
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

                sync_op = msg.record.data["_valmi_meta"]["_valmi_sync_op"]
                if not handler_response.metrics:
                    handler_response = handler_response._replace(metrics={sync_op: 1})

                for op, metric in handler_response.metrics.items():
                    counter_by_type[op] = counter_by_type[op] + metric

                # Commit state only when chunk is finished processing. Flushes are guaranteed for every chunk end, but could be more frequent and even per record for some record
                commit_state = False
                if counter % run_time_args.chunk_size == 0:
                    commit_state = True

                # Aggregate metrics for the current chunk_id and publish
                if counter % run_time_args.records_per_metric == 0 or counter % run_time_args.chunk_size == 0:
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

        handler_response = self.finalise_message_handling()
        if handler_response and handler_response.emittable_records:
            for record in handler_response.emittable_records:
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=record,
                )

        if handler_response:
            for op, metric in handler_response.metrics.items():
                counter_by_type[op] = counter_by_type[op] + metric

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
