import os

from prometheus_client import push_to_gateway, Gauge, CollectorRegistry


def get_metric_pushgateway():
    return os.getenv('PS_METRIC_PUSHGATEWAY', 'http://localhost:9091')


class ExperimentMetricsLogger:
    """Prometheus wrapper for logging custom experiment metrics
    
    Examples:
        >>> from gradient_sdk import ExperimentMetricsLogger
        >>> m_logger = ExperimentMetricsLogger("some_id")
        >>> m_logger.add_metric("some_metric_name")
        >>> m_logger["some_metric_0"] = 2
        >>> m_logger["some_metric_1"].set(3)
        >>> m_logger["some_metric_2"].inc()
        >>> m_logger["some_metric_3"].set_to_current_time()
        >>> m_logger.push_metrics()

    """

    def __init__(self, experiment_id: str, registry=CollectorRegistry(), grouping_key: dict = None):
        self.experiment_id = experiment_id
        self.registry = registry
        self.grouping_key = grouping_key

        self._metrics = dict()

    def __getitem__(self, item: str) -> Gauge:
        return self._metrics[item]

    def __setitem__(self, key: str, value):
        gauge = self[key]
        gauge.set(value)

    def add_metric(self, name: str):
        new_metric = Gauge(name, documentation="", registry=self.registry)
        self._metrics[name] = new_metric

    def push_metrics(self):
        metric_pushgateway = get_metric_pushgateway()
        push_to_gateway(
            gateway=metric_pushgateway,
            job=self.experiment_id,
            registry=self.registry,
            grouping_key=self.grouping_key,
        )
