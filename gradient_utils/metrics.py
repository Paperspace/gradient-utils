import os
from numbers import Number

from prometheus_client import push_to_gateway, Gauge, CollectorRegistry, Counter, Summary, Histogram, Info, REGISTRY

PUSH_GATEWAY_ENV = 'PAPERSPACE_METRIC_PUSHGATEWAY'
PUSH_GATEWAY_DEFAULT = 'http://prom-aggregation-gateway:80'
WORKLOAD_TYPE_ENV = 'PAPERSPACE_METRIC_WORKLOAD_TYPE'
WORKLOAD_TYPE_DEFAULT = 'experiment'
WORKLOAD_ID_ENV = 'PAPERSPACE_METRIC_WORKLOAD_ID'
LEGACY_EXPERIMENT_ID_ENV = 'PAPERSPACE_EXPERIMENT_ID'
HOSTNAME = os.getenv("HOSTNAME") or 'test-server.lan'


def get_metric_pushgateway():
    return os.getenv(PUSH_GATEWAY_ENV, PUSH_GATEWAY_DEFAULT)


def get_workload_type():
    return os.getenv(WORKLOAD_TYPE_ENV, WORKLOAD_TYPE_DEFAULT)


def get_workload_label():
    return 'label_metrics_{}_handle'.format(get_workload_type())


def _get_env_var_or_raise(*env_vars):
    rv = None
    for env_var in env_vars:
        rv = os.getenv(env_var)
        if not rv:
            break

    if rv is None:
        msg = "{} environment variable(s) not found".format(
            ", ".join(env_vars))
        raise ValueError(msg)

    return rv


def _get_experiment_id():
    if os.getenv(LEGACY_EXPERIMENT_ID_ENV):
        return os.getenv(LEGACY_EXPERIMENT_ID_ENV)
    try:
        experiment_id = HOSTNAME.split('-')[1]
        return experiment_id
    except IndexError:
        msg = "Experiment ID not found"
        raise ValueError(msg)


def get_workload_id():
    if os.getenv(WORKLOAD_ID_ENV):
        return os.getenv(WORKLOAD_ID_ENV)
    return _get_experiment_id()


def add_metrics(
        metrics,
        push_gateway=None,
        timeout=30):
    metrics_logger = MetricsLogger(push_gateway=push_gateway)

    metrics = [Metric(key, value) for key, value in metrics.items()]
    for metric in metrics:
        metrics_logger.add_gauge(metric.key)
        metrics_logger[metric.key].set(metric.value)

    metrics_logger.push_metrics(timeout)


class Metric:
    def __init__(self, key, value):
        # # TODO: Is there a way get the setters to do the initialization checks?
        # if not isinstance(key, str):
        #     raise ValueError('Key of a metric can only be a string')
        # if not isinstance(value, Number):
        #     raise ValueError('Value of a metric can only be a number')
        self.key = key
        self.value = value

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, k):
        if not isinstance(k, str):
            raise ValueError('Key of a metric can only be a string')
        self._key = k

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if not isinstance(v, Number):
            raise ValueError('Value of a metric can only be a number')
        self._value = v


class MetricsLogger:
    """Prometheus wrapper for logging custom metrics

    Examples:
        >>> from gradient_utils import MetricsLogger
        >>> m_logger = MetricsLogger()
        >>> m_logger.add_gauge("some_metric_1")
        >>> m_logger.add_gauge("some_metric_2")
        >>> m_logger["some_metric_1"].set(3)
        >>> m_logger["some_metric_1"].inc()
        >>> m_logger["some_metric_2"].set_to_current_time()
        >>> m_logger.push_metrics()
    """

    def __init__(self, workload_id=None, registry=REGISTRY, push_gateway=None):
        """
        :param str workload_id:
        :param CollectorRegistry registry:
        :param str push_gateway:
        """
        self.id = workload_id or get_workload_id()
        self.registry = registry
        self.grouping_key = {get_workload_label(): self.id}
        self.push_gateway = push_gateway or get_metric_pushgateway()

        self._metrics = dict()

    def __getitem__(self, item):
        """
        :param str item:

        :rtype Gauge|Counter|Summary|Histogram|Info
        """
        return self._metrics[item].labels(self.id, HOSTNAME)

    def add_gauge(self, name):
        self._add_metric(Gauge, name)

    def add_counter(self, name):
        self._add_metric(Counter, name)

    def add_summary(self, name):
        self._add_metric(Summary, name)

    def add_histogram(self, name):
        self._add_metric(Histogram, name)

    def add_info(self, name):
        self._add_metric(Info, name)

    def _add_metric(self, cls, name, documentation=""):
        new_metric = cls(
            name,
            documentation=documentation,
            registry=self.registry,
            labelnames=[
                get_workload_label(),
                "pod"])
        self._metrics[name] = new_metric

    def push_metrics(self, timeout=30):
        push_to_gateway(
            gateway=self.push_gateway,
            job=self.id,
            registry=self.registry,
            grouping_key=self.grouping_key,
            timeout=timeout,
        )
