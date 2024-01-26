"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

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

import importlib
import os
import shutil
from os.path import basename, isfile, join
from urllib3.util.retry import Retry

from dagster import repository
import glob
from dagster import DefaultSensorStatus, run_status_sensor, RunStatusSensorContext, DagsterRunStatus, JobSelector
import requests
from requests.adapters import HTTPAdapter

GENERATED_DIR = "generated"
CONFIG_DIR = "config"
CATALOG_DIR = "catalog"
SHARED_DIR = "/tmp/shared_dir"
APP = "valmi"
REPO_DIR = "repo"


# read the dagster jobs from storage
def get_dagster_jobs():
    repo_dir = join(SHARED_DIR, APP, REPO_DIR)
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    shutil.unpack_archive(
        join(SHARED_DIR, f"{APP}-valmi-jobs.zip"),
        repo_dir,
    )
    for f in glob.iglob(f"{repo_dir}/**/*.json", recursive=True):
        os.chmod(f, 0o766)

    # shutil.move(join(SHARED_DIR, APP, "repo", GENERATED_DIR), join(dirname(__file__), GENERATED_DIR))


def get_jobs_schedules_from_py_files(files):
    imports = [basename(f)[:-3] for f in files if isfile(f) and not f.endswith("__init__.py")]

    module_specs = [
        importlib.util.spec_from_file_location(mod, join(SHARED_DIR, APP, REPO_DIR, GENERATED_DIR, f"{mod}.py"))
        for mod in imports
    ]
    modules = [importlib.util.module_from_spec(module_spec) for module_spec in module_specs]

    for idx, module_spec in enumerate(module_specs):
        module_spec.loader.exec_module(modules[idx])

    jobs = [getattr(mod, "job") for mod in modules]
    schedules = [getattr(mod, "schedule") for mod in modules] 
    sensors = {"failure_sensor": finalise_on_run_failure,
               "canceled_sensor": finalise_on_run_canceled}

    return {
        "jobs": dict(zip([f"{file}" for file in imports], jobs)),
        "schedules": dict(zip([f"{file}_schedule" for file in imports], schedules)),
        "sensors": sensors
    }


@run_status_sensor(name="canceled_sensor", run_status=DagsterRunStatus.CANCELED,
                   default_status=DefaultSensorStatus.RUNNING, minimum_interval_seconds=3)
def finalise_on_run_canceled(context: RunStatusSensorContext):
    context.log.info("finalizer on run cancel")
    finalise_this_run(context.dagster_run.job_name)


@run_status_sensor(name="failure_sensor", run_status=DagsterRunStatus.FAILURE,
                   default_status=DefaultSensorStatus.RUNNING, minimum_interval_seconds=3)
def finalise_on_run_failure(context: RunStatusSensorContext):
    context.log.info("finalizer on run failure")
    finalise_this_run(context.dagster_run.job_name)


def finalise_this_run(job_name: str):
    activation_url = os.environ["ACTIVATION_ENGINE_URL"]
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    sync_id = job_name.replace("_", "-")
    response = session.get(f"{activation_url}/syncs/{sync_id}/runs/finalise_last_run")
    response.raise_for_status()


@repository
def valmi_repo():
    if "DAGSTER_RUN_JOB_NAME" in os.environ:
        # return only one job here
        files = [join(SHARED_DIR, APP, REPO_DIR, GENERATED_DIR, f"{os.environ['DAGSTER_RUN_JOB_NAME']}.py")]
        return get_jobs_schedules_from_py_files(files)
    else:
        get_dagster_jobs()

        import glob

        files = glob.glob(join(SHARED_DIR, APP, REPO_DIR, GENERATED_DIR, "*.py"))
        return get_jobs_schedules_from_py_files(files)
