import importlib
import os
import shutil
from os.path import basename, isfile, join

from dagster import repository

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

    return {
        "jobs": dict(zip([f"{file}" for file in imports], jobs)),
        "schedules": dict(zip([f"{file}_schedule" for file in imports], schedules)),
    }


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
