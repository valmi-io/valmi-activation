import json
import logging
import os
import shutil
import threading
import time
from os.path import dirname, join

import requests
from dagster_graphql import DagsterGraphQLClient, ShutdownRepositoryLocationInfo, ShutdownRepositoryLocationStatus
from jinja2 import Environment, FileSystemLoader
from pydantic import Json
from vyper import v

logger = logging.getLogger(v.get("LOGGER_NAME"))
GENERATED_DIR = "generated"
GENERATED_CONFIG_DIR = "config"
GENERATED_CATALOG_DIR = "catalog"
PREFIX_DIR = "/tmp"


class JobCreatorThread(threading.Thread):
    def __init__(self, threadID: int, name: str, dagster_client) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.exitFlag = False
        self.name = name
        self.dagster_client = dagster_client

    def run(self) -> None:
        while not self.exitFlag:
            try:
                resp = requests.get(f"http://{v.get('APP_BACKEND')}:{v.get('APP_BACKEND_PORT')}/api/v1/auth/syncs")

                # TODO: improve strategy to detect new syncs
                syncs_changed: bool = False
                try:
                    with open(join(PREFIX_DIR, f"{v.get('APP')}-syncs.json"), "r") as f:
                        if (f.read()) != resp.text:
                            syncs_changed = True
                except FileNotFoundError:
                    logging.exception("syncs.json not found")
                    syncs_changed = True

                # if new syncs are found, generate dagster jobs and restart dagster repository
                if syncs_changed:
                    logger.info("New syncs found")

                    # create directories for jobs, config and catalog
                    dirs = {
                        GENERATED_DIR: join(PREFIX_DIR, v.get("APP"), GENERATED_DIR),
                        GENERATED_CONFIG_DIR: join(PREFIX_DIR, v.get("APP"), GENERATED_CONFIG_DIR),
                        GENERATED_CATALOG_DIR: join(PREFIX_DIR, v.get("APP"), GENERATED_CATALOG_DIR),
                    }
                    for key in dirs.keys():
                        dir = dirs[key]
                        if os.path.exists(dir):
                            shutil.rmtree(dir)
                        os.makedirs(dir)

                    self.gen_dagster_job_archive(dirs, resp.json())

                    # restart dagster repository
                    shutdown_info: ShutdownRepositoryLocationInfo = self.dagster_client.shutdown_repository_location(
                        v.get("REPO_NAME")
                    )
                    if shutdown_info.status == ShutdownRepositoryLocationStatus.SUCCESS:
                        logger.info("Dagster repo successfully shutdown")
                    else:
                        raise Exception(f"Repository location shutdown failed: {shutdown_info.message}")

                    with open(join(PREFIX_DIR, f'{v.get("APP")}-syncs.json'), "w") as replace_file:
                        replace_file.write(resp.text)

            except Exception:
                logger.exception("Error while fetching sync jobs and creating dagster jobs")
            time.sleep(5)

    # make a zip archive of all dagster jobs
    def gen_dagster_job_archive(self, dirs: dict[str, str], syncs: Json[any]) -> None:
        for sync in syncs["syncs"]:
            self.gen_job_file(dirs, sync)
        shutil.make_archive(join(PREFIX_DIR, f"{v.get('APP')}-valmi-jobs"), "zip", join(PREFIX_DIR, v.get("APP")))

    # use jinja2 to generate dagster a single job
    def gen_job_file(self, dirs: dict[str, str], sync: Json[any]) -> None:
        with open(join(dirs[GENERATED_CONFIG_DIR], f"{sync['id']}-{sync['source']['id']}.json"), "w") as f:
            f.write(json.dumps(json.loads(sync["source"]["config"])))

        with open(join(dirs[GENERATED_CATALOG_DIR], f"{sync['id']}-{sync['source']['id']}.json"), "w") as f:
            f.write(json.dumps(json.loads(sync["source"]["catalog"])))

        with open(join(dirs[GENERATED_CONFIG_DIR], f"{sync['id']}-{sync['destination']['id']}.json"), "w") as f:
            f.write(json.dumps(json.loads(sync["destination"]["config"])))

        with open(join(dirs[GENERATED_CATALOG_DIR], f"{sync['id']}-{sync['destination']['id']}.json"), "w") as f:
            f.write(json.dumps(json.loads(sync["destination"]["catalog"])))

        file_loader = FileSystemLoader(join(dirname(__file__), "templates"))
        env = Environment(loader=file_loader)
        template = env.get_template("job_template.jinja")

        output = template.render(sync=sync, app=v.get("APP"), prefix=PREFIX_DIR)
        with open(join(dirs[GENERATED_DIR], f"{sync['id']}.py"), "w") as f:
            f.write(output)


class Orchestrator:
    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(Orchestrator, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.client = DagsterGraphQLClient(v.get("DAGIT_HOST"), port_number=v.get_int("DAGIT_PORT"))
        self.jobCreatorThread = JobCreatorThread(1, "JobCreatorThread", self.client)
        self.jobCreatorThread.start()

    def destroy(self) -> None:
        self.jobCreatorThread.exitFlag = True
