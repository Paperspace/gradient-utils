import base64
import json
import logging
import os

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from gradient_sdk.exceptions import ConfigError

logger = logging.getLogger(__name__)


def _get_work_env():
    env = os.environ.get("WORK_ENV")

    if not env:
        env = "local"

    return env


def _mongo_db_host():
    return os.environ.get("MONGO_DB_HOST")


def _mongo_db_port():
    return os.environ.get("MONGO_DB_PORT")


def _experiment_name():
    return os.environ.get("EXPERIMENT_NAME")


def _get_paperspace_tf_config():
    tf_config = os.environ.get("PS_CONFIG")

    if not tf_config:
        env = _get_work_env()
        if env != "local":
            return
        else:
            raise ConfigError(
                component="TF Config",
                message="Something went wrong. Check if you set PS_CONFIG"
            )
    if tf_config:
        return json.loads(base64.urlsafe_b64decode(tf_config).decode("utf-8"))


def _check_mongo_client_connection():
    """
    Function to check if connection to mongo is possible.

    :return: bool value if ping to mongo db ended with success
    """
    mongo_status = False

    mongo_port = _mongo_db_port()
    if mongo_port:
        mongo_port = int(mongo_port)

    client = MongoClient(
        host=_mongo_db_host(),
        port=mongo_port
    )
    try:
        resp = client.db_name.command('ping')
    except ServerSelectionTimeoutError:
        logger.warning("Check mongo db connection - connection to mongo db timeout")
        return mongo_status

    if resp.get("ok"):
        mongo_status = True

    return mongo_status


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
        return "mongo://%s:%s/%s/jobs" % (mongo_host, mongo_port, experiment_name)
    else:
        error_message = "Something went wrong. " \
                        "Check os variables that are needed for constricting mongo connection string: " \
                        "- MONGO_DB_HOST: %s  " \
                        "- MONGO_DB_PORT: %s " \
                        "- EXPERIMENT_NAME: %s" % (mongo_host, mongo_port, experiment_name)
        raise ConfigError(
            component="Mongo connection",
            message=error_message
        )


def data_dir():
    return os.environ.get("PS_JOBSPACE", "/storage")


def model_dir(model_name):
    return os.path.join(os.environ.get("PS_MODEL_PATH", "/storage/models/"), model_name)


def export_dir(model_name):
    return os.path.join(os.environ.get("PS_MODEL_PATH", "/storage/models/"), model_name)


def worker_hosts():
    return os.environ.get("WORKER_HOSTS")


def ps_hosts():
    return os.environ.get("PS_HOSTS")


def task_index():
    return os.environ.get("INDEX")


def job_name():
    return os.environ.get("TYPE")
