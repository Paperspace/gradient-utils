from numbers import Number
from prometheus_client import push_to_gateway, Gauge, CollectorRegistry, Counter, Summary, Histogram, Info
from .env import get_workload_id, get_workload_label, get_metric_pushgateway, HOSTNAME
import logging

logger = logging.getLogger(__name__)


def _get_default_grouping_key(workload_id=None, step=None):
    return {
        get_workload_label(): workload_id or get_workload_id(),
        'step': step,
    }


def add_metrics(
        metrics_map,
        step=None,
        timeout=30):
    metrics = [Metric(key, value) for key, value in metrics_map.items()]
    default_grouping_key = _get_default_grouping_key(step=step)
    for metric in metrics:
        registry = CollectorRegistry(auto_describe=True)
        new_metric_raw = Gauge(
            metric.key,
            documentation="",
            registry=registry,
            labelnames=[
                get_workload_label(),
                "pod",
                "step"])
        new_metric = new_metric_raw.labels(get_workload_id(), HOSTNAME, step)
        new_metric.set(metric.value)
        new_grouping_key = {
            "name": metric.key,
        }
        new_grouping_key.update(default_grouping_key)
        logger.debug("Setting metric key: %s, value: %s", metric.key, metric.value)
        push_to_gateway(
            gateway=get_metric_pushgateway(),
            job=get_workload_id(),
            registry=registry,
            grouping_key=new_grouping_key,
            timeout=timeout,
        )


class Metric:
    def __init__(self, key, value, step=None):
        self.key = key
        self.value = value
        self.step = step

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

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, v):
        if v is not None and (not isinstance(v, int) or v < 0):
            raise ValueError('Step can only be an integer >= 0')
        self._step = v


class MetricsLogger:
    """Prometheus wrapper for logging custom metrics

    Examples:
        >>> from gradient_utils.metrics import MetricsLogger
        >>> m_logger = MetricsLogger()
        >>> m_logger.add_gauge("some_metric_1")
        >>> m_logger.add_gauge("some_metric_2")
        >>> m_logger["some_metric_1"].set(3)
        >>> m_logger["some_metric_1"].inc()
        >>> m_logger["some_metric_2"].set_to_current_time()
        >>> m_logger.push_metrics()
    """

    def __init__(
            self,
            workload_id=None,
            registry=None,
            push_gateway=None,
            step=None):
        """
        :param str workload_id:
        :param CollectorRegistry registry:
        :param str push_gateway:
        :param int step:
        """
        self.id = workload_id or get_workload_id()
        self._registry = registry or CollectorRegistry(auto_describe=True)
        self._step = step
        self._grouping_key = _get_default_grouping_key(self.id, self._step)
        self._push_gateway = push_gateway or get_metric_pushgateway()
        self._metrics = dict()

    def __getitem__(self, item):
        """
        :param str item:

        :rtype Gauge|Counter|Summary|Histogram|Info
        """
        return self._metrics[item]

    def set_step(self, step):
        self._step = step
        self._grouping_key.update({
            'step': step,
        })

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
            registry=self._registry,
            labelnames=[
                get_workload_label(),
                "pod",
                "step"])
        self._metrics[name] = new_metric.labels(self.id, HOSTNAME, self._step)

    def push_metrics(self, timeout=30):
        push_to_gateway(
            gateway=self._push_gateway,
            job=self.id,
            registry=self._registry,
            grouping_key=self._grouping_key,
            timeout=timeout,
        )
