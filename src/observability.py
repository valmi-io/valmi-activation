import logging
from typing import Iterable


from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry import _logs

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.metrics import (
    CallbackOptions,
    Observation,
    set_meter_provider,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from fastapi import FastAPI
import os
from vyper import v

def observable_counter_func(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(1, {})


def setup_observability(app: FastAPI):
    if os.environ.get('OTEL_FASTAPI_INSTRUMENT', False) is True:
        trace.set_tracer_provider(TracerProvider())
        otlp_exporter = OTLPSpanExporter()
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        exporter = OTLPMetricExporter()
        reader = PeriodicExportingMetricReader(exporter)
        provider = MeterProvider(metric_readers=[reader])
        set_meter_provider(provider)

        FastAPIInstrumentor.instrument_app(app)

        ########
        # Logs # - OpenTelemetry Logs are still in the "experimental" state, so function names may change in the future
        ########
        
        # Initialize logging and an exporter that can send data to an OTLP endpoint by attaching OTLP handler to root logger
        _logs.set_logger_provider(LoggerProvider())

        # TODO:Setting the log format to include trace_id, span_id, and resource.service.name. But, this is formatting is not supported yet in OTLPExporter.
        format_str = os.environ.get('OTEL_PYTHON_LOG_FORMAT',
                                    "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s] - %(message)s")    
        '''
        # TODO: This is not working. Check this. The root handler is duplicating the logs. Disabled root hander.
        # Adding Handler to root logger
        root_log_handler = LoggingHandler(
            logger_provider=_logs.get_logger_provider().add_log_record_processor(
                BatchLogRecordProcessor(OTLPLogExporter())
            )
        )
        root_log_handler.setFormatter(format_str)
        logging.getLogger().addHandler(
            root_log_handler
        )
        '''

        # Adding Handler to core.engine_api
        valmi_log_handler = LoggingHandler(
            logger_provider=_logs.get_logger_provider().add_log_record_processor(
                BatchLogRecordProcessor(OTLPLogExporter())
            )
        )
        valmi_log_handler.setFormatter(logging.Formatter(format_str))
        valmi_log_handler.setLevel(os.environ.get('OTEL_PYTHON_LOG_LEVEL', "debug").upper())
        logging.getLogger(v.get("LOGGER_NAME")).addHandler(
            valmi_log_handler
        )
