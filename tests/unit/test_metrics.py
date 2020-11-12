import mock
import pytest

from gradient_utils.metrics import get_metric_pushgateway, CollectorRegistry, add_metrics

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
