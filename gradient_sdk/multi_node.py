import json
import os

from gradient_sdk.exceptions import ConfigError
from gradient_sdk.utils import _get_paperspace_tf_config


def get_tf_config():
    """
    Function to prepare TensorFlow config and set os env with proper configuration

    :raise: ConfigError when there is no configuration for TensorFlow to set as os env
    """
    tf_config = _get_paperspace_tf_config()
    if tf_config:
        os.environ['TF_CONFIG'] = json.dumps(tf_config)
    else:
        raise ConfigError(
            component="TF Config",
            message="Something went wrong. For some reason there is no configuration for TensorFlow."
        )
