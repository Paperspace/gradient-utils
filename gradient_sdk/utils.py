import base64
import json
import os


def _worker_hosts():
    return os.environ.get("WORKER_HOSTS", "")


def _ps_hosts():
    return os.environ.get("PS_HOSTS", "")


def _task_index():
    return os.environ.get("INDEX", "")


def _job_name():
    return os.environ.get("TYPE", "")


def _data_dir():
    return os.path.abspath(os.environ.get("PS_JOBSPACE", ""))


def _model_dir(model_name):
    return os.path.join(os.environ.get("PS_MODEL_PATH", ""), model_name)


def _export_dir(model_name):
    return os.path.join(os.environ.get("PS_MODEL_PATH", ""), model_name)


def _mongo_db_host():
    return os.environ["MONGO_DB_HOST"]


def _mongo_db_port():
    return os.environ["MONGO_DB_PORT"]


def _experiment_name():
    return os.environ.get("EXPERIMENT_NAME")


def _get_paperspace_tf_config():
    tf_config = os.environ.get("PS_CONFIG")

    if not tf_config:
        return

    paperspace_tf_config = json.loads(base64.urlsafe_b64decode(tf_config).decode("utf-8"))

    return paperspace_tf_config


def get_mongo_conn_str():
    return f"mongo://{_mongo_db_host()}:{_mongo_db_port()}/{_experiment_name()}/jobs"
