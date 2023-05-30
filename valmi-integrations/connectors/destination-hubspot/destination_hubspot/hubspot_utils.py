from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, Mapping

from airbyte_cdk import AirbyteLogger
import requests

from valmi_connector_lib.common.run_time_args import RunTimeArgs
from .http_sink import HttpSink
from .retry_decorators import retry_on_exception, retry_on_unauthorized_exception, RequestUnAuthorizedException
from hubspot.auth.oauth import TokensApi
from valmi_connector_lib.common.metrics import get_metric_type

from valmi_connector_lib.valmi_protocol import (
    DestinationSyncMode,
    ValmiSink,
    ValmiDestinationCatalog,
    ValmiStream,
    ConfiguredValmiSink,
    FieldCatalog,
    ValmiRejectedRecordMessage,
)

logger = AirbyteLogger()

API_URL = "https://api.hubapi.com"
REQ_TIMEOUT = 15


class HubspotClient:
    max_items_in_batch = 100

    access_token = None
    access_token_expires_in = None
    access_token_created_at = None

    def object_map(self):
        return {
            "Contact": {
                "props_url": "/crm/v3/properties/contacts",
                "batch_create_url": "/crm/v3/objects/contacts/batch/create",
                "batch_update_url": "/crm/v3/objects/contacts/batch/update",
                "read_url": "/crm/v3/objects/contacts/batch/read",
                "supported_destination_ids": {
                    DestinationSyncMode.upsert.value: ["email"],
                    DestinationSyncMode.update.value: ["id"],
                },
                "read_object_fn": self.get_objects,
            },
            "Company": {
                "props_url": "/crm/v3/properties/companies",
                "batch_create_url": "/crm/v3/objects/companies/batch/create",
                "batch_update_url": "/crm/v3/objects/companies/batch/update",
                "read_url": "/crm/v3/objects/companies/batch/read",
                "supported_destination_ids": {
                    DestinationSyncMode.upsert.value: ["domain"],
                    DestinationSyncMode.update.value: ["id"],
                },
                "read_object_fn": self.get_objects,
            },
        }

    def __init__(self, run_time_args: RunTimeArgs, *args, **kwargs):
        self.buffer = []
        self.original_records = []
        self.http_sink = HttpSink(run_time_args=run_time_args)
        self.run_time_args = run_time_args

    def map_data(self, configured_stream: ValmiStream, sink: ConfiguredValmiSink, mapping: Dict[str, str], data: Dict[str, Any]):
        mapped_data = {}
        for item in mapping:
            k = item["stream"]
            v = item["sink"]
            if k in data:
                mapped_data[v] = data[k]
        mapped_data[sink.destination_id] = data[configured_stream.id_key]
        return mapped_data

    @retry_on_exception
    def get_access_token_with_retry(self, config: Mapping[str, Any]):
        return self.get_access_token(config)
    
    def get_access_token(self, config: Mapping[str, Any]):
        if (
            self.access_token_created_at is not None
            and self.access_token_expires_in is not None
            and self.access_token_created_at + timedelta(seconds=self.access_token_expires_in) > datetime.now()
        ):
            pass
        else:
            self.access_token_created_at = datetime.now()

            resp = TokensApi().create_token(
                grant_type="refresh_token",
                client_id=config["credentials"]["client_id"],
                client_secret=config["credentials"]["client_secret"],
                refresh_token=config["credentials"]["refresh_token"],
                _request_timeout=REQ_TIMEOUT,
            )

            self.access_token = resp.access_token
            self.access_token_expires_in = resp.expires_in

    def add_to_queue(
        self, sync_op, counter, msg,
        config: Mapping[Dict, Any],
        configured_stream: ValmiStream,
        sink: ConfiguredValmiSink
    ) -> bool:
        obj = self.map_data(configured_stream, sink, sink.mapping, msg.record.data)
        
        props = {"properties": obj}
        if (sink.destination_id == "id"):
            props["id"] = obj["id"]
            del obj["id"]

        self.buffer.append(props)
        self.original_records.append(msg)

        flushed = False
        metrics = {get_metric_type(sync_op): 0}
        rejected_records = []

        if len(self.buffer) >= self.max_items_in_batch or counter % self.run_time_args.chunk_size == 0:
            flushed, metrics, rejected_records = self.flush(sync_op, config, sink)
        return flushed, metrics, rejected_records


    
    '''
    Sample Response
        {
        "status": "COMPLETE",
        "results": [
            {
                "id": "151",
                "properties": {
                    "createdate": "2023-05-30T14:29:03.906Z",
                    "email": "admin-changeme@valmi.io",
                    "hs_object_id": "151",
                    "lastmodifieddate": "2023-05-30T14:29:11.158Z"
                },
                "createdAt": "2023-05-30T14:29:03.906Z",
                "updatedAt": "2023-05-30T14:29:11.158Z",
                "archived": false
            },
            {
                "id": "101",
                "properties": {
                    "createdate": "2023-05-30T14:29:03.906Z",
                    "email": "raj+1@valmi.io",
                    "hs_object_id": "101",
                    "lastmodifieddate": "2023-05-30T14:29:20.476Z"
                },
                "createdAt": "2023-05-30T14:29:03.906Z",
                "updatedAt": "2023-05-30T14:29:20.476Z",
                "archived": false
            },
            {
                "id": "201",
                "properties": {
                    "createdate": "2023-05-30T14:29:03.906Z",
                    "email": "raj@valmi.io",
                    "hs_object_id": "201",
                    "lastmodifieddate": "2023-05-30T14:29:25.170Z"
                },
                "createdAt": "2023-05-30T14:29:03.906Z",
                "updatedAt": "2023-05-30T14:29:25.170Z",
                "archived": false
            }
        ],
        "numErrors": 1,
        "errors": [
            {
                "status": "error",
                "category": "OBJECT_NOT_FOUND",
                "message": "Could not get some CONTACT objects, they may be deleted or not exist. Check that ids are valid.",
                "context": {
                    "ids": [
                        "raj+3@valmi.io",
                        "raj+2@valmi.io"
                    ]
                }
            }
        ],
        "startedAt": "2023-05-30T16:56:07.367Z",
        "completedAt": "2023-05-30T16:56:07.403Z"
    }
    '''
    def get_objects(self, sink):
        ids = []
        for element in self.buffer:
            ids.append(element["properties"][sink.destination_id])

        fetch_properties = [sink.destination_id]
        resp = self.http_sink.send(
            method="POST",
            url=f"{API_URL}{self.object_map()[sink.sink.name]['read_url']}",
            data=None,
            json={"properties": fetch_properties,
                  "idProperty": sink.destination_id,
                  "inputs": [{"id": id} for id in ids]},
            headers={"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"},
            auth=None,
        )

        # insert the id from the fetch properties. This is needed for the update.
        ignored_ids = []
        if (resp.status_code == 200):
            ignored_ids = []
            resp_json = resp.json()
            self.insert_ids_into_obj_buffer(resp_json, sink)

        elif (resp.status_code == 207):
            resp_json = resp.json()
            self.insert_ids_into_obj_buffer(resp_json, sink)

            if resp_json["numErrors"] > 0:
                for error in resp_json["errors"]:
                    if error["status"] == "error":
                        for ctxt_id in error["context"]["ids"]:
                            ignored_ids.append((ctxt_id,
                                                error["category"],
                                                f'{error["category"]} - {error["message"]}',))
        elif (resp.status_code == 401):
            raise RequestUnAuthorizedException("Unauthorized")
        return ignored_ids

    def insert_ids_into_obj_buffer(self, resp_json, sink):
        for element in self.buffer:
            for result in resp_json["results"]:
                if element["properties"][sink.destination_id] == result["properties"][sink.destination_id]:
                    element["id"] = result["id"]
                    break

    def generate_rejected_message_from_record(self, record, error_code, error_msg):
        return ValmiRejectedRecordMessage(
            stream=record.stream,
            data=record.data,
            rejected=True,
            rejection_message=error_msg,
            rejection_code=error_code,
            rejection_metadata={},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        )

    # RETRYING specifically for 401. Other retries are covered in http_sink.
    @retry_on_unauthorized_exception
    def flush(self, sync_op, config: Mapping[Dict, Any], sink: ConfiguredValmiSink):
        self.get_access_token(config)
        
        ignored_ids = self.object_map()[sink.sink.name]["read_object_fn"](sink)
        # logger.debug(json.dumps({"inputs": self.buffer}))

        create_objs = []
        create_original_records = []
        update_objs = []
        update_original_records = []

        for idx, element in enumerate(self.buffer):
            for ignored_obj in ignored_ids:
                if element["properties"][sink.destination_id] == ignored_obj[0]:
                    create_objs.append(element)
                    create_original_records.append((self.original_records[idx], ignored_obj,))
                    break

        for idx, element in enumerate(self.buffer):
            update = True
            for ignored_obj in ignored_ids:
                if element["properties"][sink.destination_id] == ignored_obj[0]:
                    update = False
            if update:
                update_objs.append(element)
                update_original_records.append(self.original_records[idx])
                
        rejected_records = []
        metrics = defaultdict(lambda: 0)
        flushed = True

        if sync_op == DestinationSyncMode.upsert.value:
            flushed, new_metrics, new_rejected_records = self.handle_create(create_objs,
                                                                            create_original_records,
                                                                            config,
                                                                            sink)
            metrics = {**metrics, **new_metrics}
            rejected_records.extend(new_rejected_records)

            flushed, new_metrics, new_rejected_records = self.handle_update(update_objs,
                                                                            update_original_records,
                                                                            config,
                                                                            sink)
            metrics = {**metrics, **new_metrics}
            rejected_records.extend(new_rejected_records)
        elif sync_op == DestinationSyncMode.update.value:
            for idx, (original_record, ignored_obj) in enumerate(create_original_records):
                rejected_records.append(self.generate_rejected_message_from_record(original_record.record,
                                                                                   ignored_obj[1],
                                                                                   ignored_obj[2]))
            metrics[get_metric_type("ignore")] += len(create_original_records)
            flushed, new_metrics, new_rejected_records = self.handle_update(update_objs, update_original_records, config, sink)
            metrics = {**metrics, **new_metrics}
            rejected_records.extend(new_rejected_records)

        self.buffer.clear()
        self.original_records.clear()
        return flushed, metrics, rejected_records

    def handle_update(self, update_objs, update_original_records, config: Mapping[Dict, Any], sink: ConfiguredValmiSink):

        resp = self.http_sink.send(
                            method="POST",
                            url=f"{API_URL}{self.object_map()[sink.sink.name]['batch_update_url']}",
                            data=None,
                            json={"inputs": update_objs},
                            headers={"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"},
                            auth=None,
                        )
        
        rejected_records = []
        metrics = defaultdict(lambda: 0)
        if (resp.status_code == 207):
            resp_json = resp.json()
            if resp_json["numErrors"] > 0:
                for error in resp_json["errors"]:
                    if error["status"] == "error":
                        for ctxt_id in error["context"]["ids"]:
                            for idx, element in enumerate(update_objs):
                                rejected_records.append(
                                    self.generate_rejected_message_from_record(update_original_records[idx].record, error["category"], f'{error["category"]} - {error["message"]}'))
                                    
        elif (resp.status_code == 401):
            raise RequestUnAuthorizedException("Unauthorized")
        
        metrics[get_metric_type("update")] += len(update_objs) - len(rejected_records)
        metrics[get_metric_type("fail")] += len(rejected_records)

        return True, metrics, rejected_records

    def handle_create(self, update_objs, update_original_records, config: Mapping[Dict, Any], sink: ConfiguredValmiSink):

        resp = self.http_sink.send(
                            method="POST",
                            url=f"{API_URL}{self.object_map()[sink.sink.name]['batch_create_url']}",
                            data=None,
                            json={"inputs": update_objs},
                            headers={"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"},
                            auth=None,
                        )
        
        rejected_records = []
        metrics = defaultdict(lambda: 0)
        if (resp.status_code == 207):
            resp_json = resp.json()
            if resp_json["numErrors"] > 0:
                for error in resp_json["errors"]:
                    if error["status"] == "error":
                        for ctxt_id in error["context"]["ids"]:
                            for idx, element in enumerate(update_objs):
                                rejected_records.append(
                                    self.generate_rejected_message_from_record(update_original_records[idx].record, error["category"], f'{error["category"]} - {error["message"]}'))
                                    
        elif (resp.status_code == 401):
            raise RequestUnAuthorizedException("Unauthorized")
        
        metrics[get_metric_type("upsert")] += len(update_objs) - len(rejected_records)
        metrics[get_metric_type("fail")] += len(rejected_records)

        return True, metrics, rejected_records

         
    def get_sinks(self, config: Mapping[str, Any]):
        # api_client = ApiClient()
        self.get_access_token(config)

        sinks = []
        for k, v in self.object_map().items():
            obj_name = k
            obj_id = k
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
            }

            props_url = v["props_url"]
            resp = requests.get(
                f"{API_URL}{props_url}", timeout=REQ_TIMEOUT, headers={"Authorization": f"Bearer {self.access_token}"}
            ).json()

            #print(json.dumps(resp, indent=4))

            for result in resp["results"]:
                if "modificationMetadata" in result and result["modificationMetadata"]["readOnlyValue"]:
                    continue
                if result["hidden"] or result["calculated"] or not result["formField"]:
                    continue

                json_schema["properties"][result["name"]] = {}
                json_schema["properties"][result["name"]]["type"] = result["type"]
                json_schema["properties"][result["name"]]["description"] = result["description"]
                json_schema["properties"][result["name"]]["label"] = result["label"]

            sinks.append(
                ValmiSink(
                    name=f"{obj_name}",
                    id=f"{obj_id}",
                    supported_destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.update],
                    field_catalog={
                        DestinationSyncMode.upsert.value: FieldCatalog(
                            json_schema=json_schema,
                            allow_freeform_fields=False,
                            supported_destination_ids=v["supported_destination_ids"][DestinationSyncMode.upsert.value],
                        ),
                        DestinationSyncMode.update.value: FieldCatalog(
                            json_schema=json_schema,
                            allow_freeform_fields=False,
                            supported_destination_ids=v["supported_destination_ids"][DestinationSyncMode.update.value],
                        ),
                    },
                )
            )
        return ValmiDestinationCatalog(sinks=sinks)
