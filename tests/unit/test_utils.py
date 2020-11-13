import os

import pytest

from gradient_utils.exceptions import ConfigError
from gradient_utils.utils import get_mongo_conn_str, data_dir, model_dir, export_dir


def test_get_mongo_conn_str_default():
    with pytest.raises(ConfigError) as ce:
        _ = get_mongo_conn_str()

    assert "Something went wrong. " in str(ce.value)


def test_get_mongo_conn_str():
    os.environ["MONGO_DB_HOST"] = "localhost"
    os.environ["MONGO_DB_PORT"] = "27017"
    os.environ["EXPERIMENT_NAME"] = "test"

    conn_str = get_mongo_conn_str()

    assert "mongo://localhost:27017/test/jobs" == conn_str

    os.environ.pop("MONGO_DB_HOST")
    os.environ.pop("MONGO_DB_PORT")
    os.environ.pop("EXPERIMENT_NAME")


def test_data_dir_default():
    data_path = data_dir()

    assert "/storage" == data_path


def test_data_dir():
    os.environ["PS_JOBSPACE"] = "/test"
    data_path = data_dir()

    assert "/test" == data_path

    os.environ.pop("PS_JOBSPACE")


def test_model_dir_default():
    if "PS_MODEL_PATH" in os.environ:
        del os.environ["PS_MODEL_PATH"]

    model_path = model_dir("test")

    assert "/storage/models/test" == model_path


def test_model_dir():
    os.environ["PS_MODEL_PATH"] = "/models"

    model_path = model_dir("test")

    assert "/models/test" == model_path

    os.environ.pop("PS_MODEL_PATH")


def test_export_dir_default():
    model_path = export_dir("test")

    assert "/storage/models/test" == model_path


def test_export_dir():
    os.environ["PS_MODEL_PATH"] = "/models"

    model_path = export_dir("test")

    assert "/models/test" == model_path

    os.environ.pop("PS_MODEL_PATH")
