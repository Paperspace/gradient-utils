from unittest import mock

from gradient_sdk import ExperimentMetricsLogger
from gradient_sdk.metrics import get_metric_pushgateway, CollectorRegistry


@mock.patch("gradient_sdk.metrics.Gauge")
def test_should_create_metrics_logger_instance_with_required_parameters(gauge_patched):
    metrics_logger = ExperimentMetricsLogger("some_id")

    assert metrics_logger.experiment_id == "some_id"
    assert metrics_logger.grouping_key is None
    assert isinstance(metrics_logger.registry, CollectorRegistry)


@mock.patch("gradient_sdk.metrics.Gauge")
def test_should_create_metrics_logger_instance_with_all_parameters(gauge_patched):
    grouping_key = {"key": "value"}
    registry = CollectorRegistry()

    metrics_logger = ExperimentMetricsLogger(
        "some_id",
        registry=registry,
        grouping_key=grouping_key,
    )

    assert metrics_logger.experiment_id == "some_id"
    assert metrics_logger.grouping_key == grouping_key
    assert metrics_logger.registry is registry


@mock.patch("gradient_sdk.metrics.Gauge")
def test_should_add_metrics_to_logger_instance(gauge_patched):
    grouping_key = {"key": "value"}
    registry = CollectorRegistry()
    metrics_logger = ExperimentMetricsLogger(
        "some_id",
        registry=registry,
        grouping_key=grouping_key,
    )

    metrics_logger.add_metric("some_metric")

    assert "some_metric" in metrics_logger._metrics
    gauge_patched.assert_called_once_with(
        "some_metric",
        documentation="",
        registry=registry,
    )


@mock.patch("gradient_sdk.metrics.Gauge")
def test_should_add_multiple_metrics_to_logger_instance(gauge_patched):
    grouping_key = {"key": "value"}
    registry = CollectorRegistry()
    metrics_logger = ExperimentMetricsLogger(
        "some_id",
        registry=registry,
        grouping_key=grouping_key,
    )

    metrics_logger.add_metric("some_metric")
    metrics_logger.add_metric("some_other_metric")

    assert "some_metric" in metrics_logger._metrics
    assert "some_other_metric" in metrics_logger._metrics
    gauge_patched.assert_has_calls([
        mock.call(
            "some_metric",
            documentation="",
            registry=registry,
        ),
        mock.call(
            "some_other_metric",
            documentation="",
            registry=registry,
        ),
    ])


@mock.patch("gradient_sdk.metrics.Gauge")
def test_should_update_metric_value(gauge_patched):
    metrics_logger = ExperimentMetricsLogger("some_id")

    metrics_logger.add_metric("some_metric")
    metrics_logger["some_metric"] = 1
    metrics_logger["some_metric"].set(2)

    gauge_patched().set.assert_has_calls([
        mock.call(1),
        mock.call(2),
    ])


@mock.patch("gradient_sdk.metrics.push_to_gateway")
def test_should_use_push_to_gateway_to_log_metrics(push_to_gateway_patched):
    grouping_key = {"key": "value"}
    registry = CollectorRegistry()
    metrics_logger = ExperimentMetricsLogger(
        "some_id",
        registry=registry,
        grouping_key=grouping_key,
    )

    metrics_logger.push_metrics()

    push_to_gateway_patched.assert_called_once_with(
        gateway=get_metric_pushgateway(),
        job="some_id",
        registry=registry,
        grouping_key=grouping_key,
    )
