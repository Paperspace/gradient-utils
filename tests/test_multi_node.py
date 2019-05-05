import os

import pytest

from gradient_sdk import get_tf_config
from gradient_sdk.exceptions import ConfigError


def test_get_tf_config_default():
    assert not os.environ.get("PS_CONFIG")
    with pytest.raises(ConfigError) as ce:
        get_tf_config()

    assert "TF Config" in str(ce.value)
    assert "Something went wrong. " in str(ce.value)


def test_get_tf_config():
    assert not os.environ.get("TF_CONFIG")

    os.environ["PS_CONFIG"] = "eyJjbHVzdGVyIjogeyJtYXN0ZXIiOiBbImxvY2FsaG9zdDo1MDAwIl0sICJ3b3JrZXIiOiBbImxvY2FsaG9zdDo1MDAwIiwgImxvY2FsaG9zdDo1MDAxIl0sICJwcyI6IFsibG9jYWxob3N0OjUwMDIiXX0sICJ0YXNrIjogeyJ0eXBlIjogIm1hc3RlciIsICJpbmRleCI6IDB9LCAiZW52aXJvbm1lbnQiOiAiY2xvdWQifQ\=\="
    get_tf_config()

    assert os.environ.get("TF_CONFIG")

    os.environ.pop("PS_CONFIG")
