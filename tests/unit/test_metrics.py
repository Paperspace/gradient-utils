import mock
import pytest

from gradient_utils.metrics import get_metric_pushgateway, CollectorRegistry, Metric
from gradient_utils.metrics import _add_metrics as add_metrics


def test_add_metrics_errors_with_nonstring_key():
    registry = CollectorRegistry()
    metrics = {
        23: 2
    }

    with pytest.raises(ValueError) as ce:
        add_metrics(metrics)

    assert "Key of a metric can only be a string" in str(ce.value)


def test_add_metrics_errors_with_nonnumber_value():
    registry = CollectorRegistry()
    metrics = {
        'catdog': '2'
    }
    with pytest.raises(ValueError) as ce:
        add_metrics(metrics)
    assert "Value of a metric can only be a number" in str(ce.value)

    metrics_obj = {
        'catdog': {'2': 2}
    }
    with pytest.raises(ValueError) as ce:
        add_metrics(metrics_obj)
    assert "Value of a metric can only be a number" in str(ce.value)

# Metric


def test_metric_creates_object():
    metric = Metric('key', 100)
    assert 'key' == metric.key
    assert 100 == metric.value


def test_metric_invalid_key():
    with pytest.raises(ValueError) as e:
        metric = Metric(100, 100)
    assert "Key of a metric can only be a string" in str(e.value)


def test_metric_invalid_value():
    with pytest.raises(ValueError) as e:
        metric = Metric('key', 'value')
    assert "Value of a metric can only be a number" in str(e.value)


def test_metric_invalid_reassign_key():
    metric = Metric('key', 100)
    with pytest.raises(ValueError) as e:
        metric.key = 1999
    assert "Key of a metric can only be a string" in str(e.value)


def test_metric_invalid_reassign_value():
    metric = Metric('key', 100)
    with pytest.raises(ValueError) as e:
        metric.value = 'value'
    assert "Value of a metric can only be a number" in str(e.value)
