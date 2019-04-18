import base64
import json
import os

from exceptions import ConfigError
# TODO set env variable for local or PS CLOUD (GCP)


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
    """
    Function to check and construct mongo db connection string.

    :raise: ConfigError with information about missing values.

    :return: Mongo connection string
    """
    mongo_host = _mongo_db_host()
    mongo_port = _mongo_db_port()
    experiment_name = _experiment_name()

    if mongo_host and mongo_port and experiment_name:
        return f"mongo://{_mongo_db_host()}:{_mongo_db_port()}/{_experiment_name()}/jobs"
    else:
        raise ConfigError(
            component="Mongo connection",
            message=f"""
            Something went wrong. Check os variables that are needed for constricting mongo connection string:
            MONGO_DB_HOST: {mongo_host}
            MONGO_DB_PORT: {mongo_port}
            EXPERIMENT_NAME: {experiment_name}
            """
        )


def data_dir():
    return os.path.abspath(os.environ.get("PS_JOBSPACE", "/storage"))


def model_dir(model_name):
    return os.path.join(os.environ.get("PS_MODEL_PATH", "/storage/models/"), model_name)


def export_dir(model_name):
    return os.path.join(os.environ.get("PS_MODEL_PATH", "/storage/models/"), model_name)


def worker_hosts():
    return os.environ.get("WORKER_HOSTS", "")


def ps_hosts():
    return os.environ.get("PS_HOSTS", "")


def task_index():
    return os.environ.get("INDEX", "")


def job_name():
    return os.environ.get("TYPE", "")
