import importlib
import shutil
from os.path import basename, dirname, isfile, join

from dagster import repository

GENERATED_DIR = "generated"


# read the dagster jobs from storage and store into GENERATED_DIR
def get_dagster_jobs():
    shutil.unpack_archive()


@repository
def deploy_docker_repository():
    import glob

    modules = glob.glob(join(dirname(__file__), GENERATED_DIR, "*.py"))
    imports = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")]
    modules = [importlib.import_module(f"valmi_repo.{GENERATED_DIR}.{mod}") for mod in imports]

    jobs = [getattr(mod, "job") for mod in modules]
    schedules = [getattr(mod, "schedule") for mod in modules]

    return {
        "jobs": dict(zip([f"{file}".capitalize() for file in imports], jobs)),
        "schedules": dict(zip([f"{file}_schedule".capitalize() for file in imports], schedules)),
    }
