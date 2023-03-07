import json
import logging
import os
import shutil
import threading
import time
from os.path import dirname, join

from dagster_graphql import DagsterGraphQLClient, ShutdownRepositoryLocationInfo, ShutdownRepositoryLocationStatus
from jinja2 import Environment, FileSystemLoader
from pydantic import Json
from vyper import v

logger = logging.getLogger(v.get("LOGGER_NAME"))
GENERATED_DIR = "generated"
GENERATED_CONFIG_DIR = "config"
GENERATED_CATALOG_DIR = "catalog"
SHARED_DIR = "/tmp/shared_dir"
dummy_json = """{
      "syncs": [
          {   "id": "syncid1234",
              "name" : "name for sync id 1234",
              "source": {
                  "name": "name for source Id 1234",
                  "id": "sourceid1234",
                  "type": "POSTGRES",
                  "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"     \\n}",
                  "catalog":"{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actorhello\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}" ,
                  "container_image": "valmi/source-postgres:dev"
              },
              "destination": {
                  "name": "name for destination Id 1234",
                  "id": "destinationid1234",
                  "type": "WEBHOOK",
                  "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
                  "catalog":"{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}" ,
                  "container_image": "valmi/destination-webhook:dev"             
                }
          },
          {   "id": "syncid2345",
              "name" : "name for sync id 2345",
              "source": {
                  "name": "name for source Id 2345",
                  "id": "sourceid2345",
                  "type": "POSTGRES",
                  "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
                  "catalog":"{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}" ,
                  "container_image": "valmi/source-postgres:dev"
              },
              "destination": {
                  "name": "name for destination Id 1234",
                  "id": "destinationid2345",
                  "type": "WEBHOOK",
                  "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
                  "catalog":"{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}" ,
                  "container_image": "valmi/destination-webhook:dev"             
                }
          },
          {   "id": "newsyncid_123",
              "name" : "name for sync id 123",
              "source": {
                  "name": "name for source Id 2345",
                  "id": "sourceid23452",
                  "type": "POSTGRES",
                  "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
                  "catalog":"{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"customer\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"email\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}" ,
                  "container_image": "valmi/source-postgres:dev"
              },
              "destination": {
                  "name": "name for destination Id 1234",
                  "id": "destinationid23452",
                  "type": "WEBHOOK",
                  "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
                  "catalog":"{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}" ,
                  "container_image": "valmi/destination-webhook:dev"             
                }
          },
          {
            "id": "newsyncid_456",
            "name": "name for sync id 123",
            "source": {
              "name": "name for source Id 2345",
              "id": "sourceid23452",
              "type": "POSTGRES",
              "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
              "catalog": "{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"customer\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"email\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}",
              "container_image": "valmi/source-postgres:dev"
            },
            "destination": {
              "name": "name for destination Id 1234",
              "id": "destinationid23452",
              "type": "WEBHOOK",
              "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 8080,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
              "catalog": "{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}",
              "container_image": "valmi/destination-webhook:dev"
            }
          },
          {
            "id": "DemoSync_12345",
            "name": "demo for sync id 123",
            "source": {
              "name": "name for source Id 2345",
              "id": "sourceid23452",
              "type": "POSTGRES",
              "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
              "catalog": "{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"country\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"country_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"country\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_update\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}",
              "container_image": "valmi/source-postgres:dev"
            },
            "destination": {
              "name": "name for destination Id 1234",
              "id": "destinationid23452",
              "type": "WEBHOOK",
              "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 8080,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
              "catalog": "{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}",
              "container_image": "valmi/destination-webhook:dev"
            }
          },
          {
            "id": "Demo_Sync_Reddy",
            "name": "demo for reddy 123",
            "source": {
              "name": "name for source Id 2345",
              "id": "sourceid23452",
              "type": "POSTGRES",
              "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
              "catalog": "{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"film\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"film_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"title\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"description\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}",
              "container_image": "valmi/source-postgres:dev"
            },
            "destination": {
              "name": "name for destination Id 1234",
              "id": "destinationid23452",
              "type": "WEBHOOK",
              "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 8080,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
              "catalog": "{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}",
              "container_image": "valmi/destination-webhook:dev"
            }
          },
          
          {
            "id": "New_Demo_Sync",
            "name": "new new demo",
            "source": {
              "name": "name for source Id 2345",
              "id": "sourceid234521",
              "type": "POSTGRES",
              "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 5432,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
              "catalog": "{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}",
              "container_image": "valmi/source-postgres:dev"
            },
            "destination": {
              "name": "name for destination Id 1234",
              "id": "destinationid23452",
              "type": "WEBHOOK",
              "config": "\\n{\\n    \\"host\\": \\"host.docker.internal\\",\\n    \\"port\\": 8080,\\n    \\"database\\": \\"dvdrental\\",\\n    \\"user\\": \\"postgres\\",\\n    \\"password\\": \\"changeme\\",\\n    \\"namespace\\" : \\"public\\"  \\n}",
              "catalog": "{\\n    \\"streams\\": [\\n        {\\n            \\"sync_mode\\": \\"full_refresh\\",\\n            \\"destination_sync_mode\\":\\"append\\",\\n            \\"stream\\": {\\n                \\"name\\": \\"actor\\",\\n                \\"supported_sync_modes\\": [\\n                    \\"full_refresh\\",\\n                    \\"incremental\\"\\n                ],\\n                \\"source_defined_cursor\\": false,\\n                \\"json_schema\\": {\\n                    \\"type\\": \\"object\\",\\n                    \\"properties\\": {\\n                        \\"first_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"last_name\\": {\\n                            \\"type\\": \\"string\\"\\n                        },\\n                        \\"actor_id\\": {\\n                            \\"type\\": \\"string\\"\\n                        }\\n                    }\\n                }\\n            }\\n        }\\n    ]\\n}",
              "container_image": "valmi/destination-webhook:dev"
            }
          }
      ]
    }"""


class Response:
    def __init__(self, text):
        self.text = text


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
                # resp = requests.get(f"http://{v.get('APP_BACKEND')}:{v.get('APP_BACKEND_PORT')}/api/v1/syncs/")
                resp = Response(dummy_json)

                # TODO: improve strategy to detect new syncs
                syncs_changed: bool = False
                try:
                    with open(join(SHARED_DIR, f"{v.get('APP')}-syncs.json"), "r") as f:
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
                        GENERATED_DIR: join(SHARED_DIR, v.get("APP"), "gen", GENERATED_DIR),
                        GENERATED_CONFIG_DIR: join(SHARED_DIR, v.get("APP"), "gen", GENERATED_CONFIG_DIR),
                        GENERATED_CATALOG_DIR: join(SHARED_DIR, v.get("APP"), "gen", GENERATED_CATALOG_DIR),
                    }
                    for key in dirs.keys():
                        dir = dirs[key]
                        if os.path.exists(dir):
                            shutil.rmtree(dir)
                        os.makedirs(dir)

                    self.gen_dagster_job_archive(dirs, json.loads(resp.text))

                    # restart dagster repository
                    shutdown_info: ShutdownRepositoryLocationInfo = self.dagster_client.shutdown_repository_location(
                        v.get("REPO_NAME")
                    )
                    if shutdown_info.status == ShutdownRepositoryLocationStatus.SUCCESS:
                        logger.info("Dagster repo successfully shutdown")
                    else:
                        raise Exception(f"Repository location shutdown failed: {shutdown_info.message}")

                    with open(join(SHARED_DIR, f'{v.get("APP")}-syncs.json'), "w") as replace_file:
                        replace_file.write(resp.text)

            except Exception:
                logger.exception("Error while fetching sync jobs and creating dagster jobs")
            time.sleep(5)

    # make a zip archive of all dagster jobs
    def gen_dagster_job_archive(self, dirs: dict[str, str], syncs: Json[any]) -> None:
        print(syncs)
        for sync in syncs["syncs"]:
            self.gen_job_file(dirs, sync)
        # with open(join(dirs[GENERATED_DIR], f"__init__.py"), "w") as f:
        #    f.write("# Autogenerated: This file is needed to make a valid python package")
        shutil.make_archive(
            join(SHARED_DIR, f"{v.get('APP')}-valmi-jobs"), "zip", join(SHARED_DIR, v.get("APP"), "gen")
        )

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

        output = template.render(sync=sync, app=v.get("APP"), prefix=SHARED_DIR)
        with open(join(dirs[GENERATED_DIR], f"{sync['id']}.py"), "w") as f:
            f.write(output)


class Repo:
    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(Repo, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.client = DagsterGraphQLClient(v.get("DAGIT_HOST"), port_number=v.get_int("DAGIT_PORT"))
        self.jobCreatorThread = JobCreatorThread(1, "JobCreatorThread", self.client)
        self.jobCreatorThread.start()

    def destroy(self) -> None:
        self.jobCreatorThread.exitFlag = True
