import json
import os

from utils import _get_paperspace_tf_config


def get_tf_config():
    tf_config = _get_paperspace_tf_config()
    if tf_config:
        os.environ['TF_CONFIG'] = json.dumps(tf_config)

    # TODO how we should handle situation where there is no tf_config?
