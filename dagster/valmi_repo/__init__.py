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


# read the dagster jobs from storage
def get_dagster_jobs():
    shutil.unpack_archive(
        join(SHARED_DIR, f"{APP}-valmi-jobs.zip"),
        join(SHARED_DIR, APP, "repo"),
    )
    # shutil.move(join(SHARED_DIR, APP, "repo", GENERATED_DIR), join(dirname(__file__), GENERATED_DIR))


@repository
def valmi_repo():
    os.system("printenv")
    if "DAGSTER_RUN_JOB_NAME" in os.environ:
        files = [join(SHARED_DIR, APP, "repo", GENERATED_DIR, f"{os.environ['DAGSTER_RUN_JOB_NAME']}.py")]
        imports = [basename(f)[:-3] for f in files if isfile(f) and not f.endswith("__init__.py")]

        module_specs = [
            importlib.util.spec_from_file_location(mod, join(SHARED_DIR, APP, "repo", GENERATED_DIR, f"{mod}.py"))
            for mod in imports
        ]
        modules = [importlib.util.module_from_spec(module_spec) for module_spec in module_specs]

        for idx, module_spec in enumerate(module_specs):
            module_spec.loader.exec_module(modules[idx])

        jobs = [getattr(mod, "job") for mod in modules]
        schedules = [getattr(mod, "schedule") for mod in modules]

        return {
            "jobs": dict(zip([f"{file}".capitalize() for file in imports], jobs)),
            "schedules": dict(zip([f"{file}_schedule".capitalize() for file in imports], schedules)),
        }

    else:
        get_dagster_jobs()

        import glob

        files = glob.glob(join(SHARED_DIR, APP, "repo", GENERATED_DIR, "*.py"))

        imports = [basename(f)[:-3] for f in files if isfile(f) and not f.endswith("__init__.py")]
        module_specs = [
            importlib.util.spec_from_file_location(mod, join(SHARED_DIR, APP, "repo", GENERATED_DIR, f"{mod}.py"))
            for mod in imports
        ]
        modules = [importlib.util.module_from_spec(module_spec) for module_spec in module_specs]

        for idx, module_spec in enumerate(module_specs):
            module_spec.loader.exec_module(modules[idx])

        # modules = [importlib.import_module(f"{GENERATED_DIR}.{mod}") for mod in imports]

        jobs = [getattr(mod, "job") for mod in modules]
        schedules = [getattr(mod, "schedule") for mod in modules]

        return {
            "jobs": dict(zip([file.capitalize() for file in imports], jobs)),
            "schedules": dict(zip([f"{file}_schedule".capitalize() for file in imports], schedules)),
        }
