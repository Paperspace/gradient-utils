import base64
import json
import os


def worker_hosts():
    return os.environ.get('WORKER_HOSTS', '')


def ps_hosts():
    return os.environ.get('PS_HOSTS', '')


def task_index():
    return os.environ.get('INDEX', '')


def job_name():
    return os.environ.get('TYPE', '')


def data_dir():
    return os.path.abspath(os.environ.get('PS_JOBSPACE', ''))


def model_dir():
    return os.path.abspath(os.environ.get('PS_MODEL_PATH', ''))  # name of the model


def export_dir():
    return os.path.abspath(os.environ.get('PS_MODEL_PATH', ''))  # name of the model


def get_paperspace_tf_config():
    tf_config = os.environ.get('TF_CONFIG')
    if not tf_config:
        return
    paperspace_tf_config = json.loads(base64.urlsafe_b64decode(tf_config).decode('utf-8'))

    return paperspace_tf_config


def get_tf_config():
    tf_config = get_paperspace_tf_config()
    if tf_config:
        os.environ['TF_CONFIG'] = json.dumps(tf_config)
