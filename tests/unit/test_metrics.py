import mock
import pytest

from gradient_utils.metrics import get_metric_pushgateway, CollectorRegistry, add_metrics

@mock.patch("gradient_utils.metrics.push_to_gateway")
@mock.patch("gradient_utils.metrics.Gauge")
def test_add_metrics_pushes_metrics(gauge_patched, push_to_gateway_patched):
    registry = CollectorRegistry()
    metrics = {
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }
    add_metrics(metrics, workload_id='some_id', registry=registry)

    # TODO: The best way to test would be to verify that the three metrics are
    #       waiting at the pushgateway.
    push_to_gateway_patched.assert_called_once_with(
        gateway=get_metric_pushgateway(),
        job="some_id",
        registry=registry,
        grouping_key={'label_metrics_experiment_handle': 'some_id'},
        timeout=30,
    )

    calls = [mock.call(1), mock.call(2), mock.call(1.2)]
    gauge_patched().labels("some_id", None).set.assert_has_calls(calls, any_order=True)

def test_add_metrics_errors_with_nonstring_key():
    registry = CollectorRegistry()
    metrics = {
        23: 2
    }

    with pytest.raises(ValueError) as ce:
        add_metrics(metrics, workload_id='some_id', registry=registry)

    assert "Key of a metric can only be a string" in str(ce.value)

def test_add_metrics_errors_with_nonnumber_value():
    registry = CollectorRegistry()
    metrics = {
        'catdog': '2'
    }
    with pytest.raises(ValueError) as ce:
        add_metrics(metrics, workload_id='some_id', registry=registry)
    assert "Value of a metric can only be a number" in str(ce.value)

    metrics_obj = {
        'catdog': {'2': 2}
    }
    with pytest.raises(ValueError) as ce:
        add_metrics(metrics_obj, workload_id='some_id', registry=registry)
    assert "Value of a metric can only be a number" in str(ce.value)
