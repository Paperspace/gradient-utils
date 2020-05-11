import os
from typing import Union

from prometheus_client import push_to_gateway, Gauge, CollectorRegistry, Counter, Summary, Histogram, Info


def get_metric_pushgateway():
    return os.getenv('PAPERSPACE_METRIC_PUSHGATEWAY', 'http://localhost:9091')


def _get_env_var_or_raise(*env_vars):
    rv = None
    for env_var in env_vars:
        rv = os.getenv(env_var)
        if not rv:
            break

    if rv is None:
        msg = "{} environment variable(s) not found".format(", ".join(env_vars))
        raise ValueError(msg)

    return rv


def get_job_id():
    return _get_env_var_or_raise("PAPERSPACE_EXPERIMENT_ID", "PAPERSPACE_DEPLOYMENT_ID")


class MetricsLogger:
    """Prometheus wrapper for logging custom metrics
    
    Examples:
        >>> from gradient_sdk import MetricsLogger
        >>> m_logger = MetricsLogger()
        >>> m_logger.add_gauge("some_metric_name")
        >>> m_logger["some_metric_1"].set(3)
        >>> m_logger["some_metric_2"].inc()
        >>> m_logger["some_metric_3"].set_to_current_time()
        >>> m_logger.push_metrics()

    """

    def __init__(self, job_id=None, registry=CollectorRegistry(), grouping_key: dict = None, push_gateway=None):
        self.id = job_id or get_job_id()
        self.registry = registry
        self.grouping_key = grouping_key
        self.push_gateway = push_gateway or get_metric_pushgateway()

        self._metrics = dict()

    def __getitem__(self, item: str) -> Union[Gauge, Counter, Summary, Histogram, Info]:
        return self._metrics[item]

    def add_gauge(self, name: str):
        self._add_metric(Gauge, name)

    def add_counter(self, name: str):
        self._add_metric(Counter, name)

    def add_summary(self, name: str):
        self._add_metric(Summary, name)

    def add_histogram(self, name: str):
        self._add_metric(Histogram, name)

    def add_info(self, name: str):
        self._add_metric(Info, name)

    def _add_metric(self, cls, name, documentation=""):
        new_metric = cls(name, documentation=documentation, registry=self.registry)
        self._metrics[name] = new_metric

    def push_metrics(self, timeout=30):
        push_to_gateway(
            gateway=self.push_gateway,
            job=self.id,
            registry=self.registry,
            grouping_key=self.grouping_key,
            timeout=timeout,
        )
