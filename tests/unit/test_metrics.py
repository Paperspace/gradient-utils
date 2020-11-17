import pytest

from gradient_utils.metrics.metrics import add_metrics, Metric
from gradient_utils.metrics import init, patched


def test_empty_init():
    init()
    assert(len(patched["tensorboard"]) == 0)


def test_init_sync_tensorboard():
    init(sync_tensorboard=True)
    assert(len(patched["tensorboard"]) > 0)


def test_add_metrics_errors_with_nonstring_key():
    metrics = {
        23: 2
    }

    with pytest.raises(ValueError) as ce:
        add_metrics(metrics)

    assert "Key of a metric can only be a string" in str(ce.value)


def test_add_metrics_errors_with_nonnumber_value():
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
    assert None is metric.step


def test_metric_invalid_key():
    with pytest.raises(ValueError) as e:
        Metric(100, 100)
    assert "Key of a metric can only be a string" in str(e.value)


def test_metric_invalid_value():
    with pytest.raises(ValueError) as e:
        Metric('key', 'value')
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


def test_metric_valid_step():
    metric = Metric('key', 100, step=1)
    assert 1 == metric.step
    metric.step = 0
    assert 0 == metric.step


def test_metric_invalid_step():
    with pytest.raises(ValueError) as e:
        Metric('key', 100, step='One')
    assert "Step can only be an integer >= 0" in str(e.value)

    with pytest.raises(ValueError) as e:
        Metric('key', 100, step=-1)
    assert "Step can only be an integer >= 0" in str(e.value)

    with pytest.raises(ValueError) as e:
        Metric('key', 100, step=2.3)
    assert "Step can only be an integer >= 0" in str(e.value)


def test_metric_invalid_changing_step():
    metric = Metric('key', 100, step=1)
    with pytest.raises(ValueError) as e:
        metric.step = 'One'
    assert "Step can only be an integer >= 0" in str(e.value)
