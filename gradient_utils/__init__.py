"""
Gradient ML SDK
"""
from gradient_utils.hyper_parameter import hyper_tune
from gradient_utils.metrics import MetricsLogger
from gradient_utils.multi_node import get_tf_config
from gradient_utils.utils import get_mongo_conn_str, data_dir, worker_hosts, export_dir, job_name, model_dir, ps_hosts, \
    task_index

# this is automatically set to the latest tagged version by CircleCI
__version__ = "0.0.1"

__all__ = [
    "__version__",
    "get_tf_config",
    "get_mongo_conn_str",
    "data_dir",
    "worker_hosts",
    "export_dir",
    "job_name",
    "model_dir",
    "ps_hosts",
    "task_index",
    "hyper_tune",
    "MetricsLogger",
]
