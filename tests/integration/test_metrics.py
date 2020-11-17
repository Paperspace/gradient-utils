import mock
import pytest
import requests
import os
from prometheus_client import delete_from_gateway

from gradient_utils.metrics import get_metric_pushgateway, CollectorRegistry, add_metrics, MetricsLogger

LOCAL_PUSH_GATEWAY = os.getenv('PAPERSPACE_METRIC_PUSHGATEWAY')


def test_add_metric_integration():
    m_logger = MetricsLogger()
    delete_from_gateway(m_logger.push_gateway, m_logger.id, grouping_key=m_logger.grouping_key)

    m_logger.add_gauge("some_metric_1")
    m_logger.add_gauge("some_metric_2")
    m_logger["some_metric_1"].set(3)
    m_logger["some_metric_1"].inc()
    m_logger.push_metrics()

    expected = {
        "some_metric_1": '4'
    }

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    gateway_metrics = r.json()['data'][0]
    for key in expected:
        # Each metric is returned in a dictionary so we need to get the singular key
        # Assert value returned by gateway matches what we provided
        assert expected[key] == gateway_metrics[key]['metrics'][0]['value']
        assert 'GAUGE' == gateway_metrics[key]['type']

    # Clean up
    delete_from_gateway(m_logger.push_gateway, m_logger.id, grouping_key=m_logger.grouping_key)


def test_add_metrics_pushes_metrics():
    # Before tests, clear the push gateway
    # TODO: Run this before each
    metrics_logger_config = MetricsLogger()
    delete_from_gateway(metrics_logger_config.push_gateway, metrics_logger_config.id, grouping_key=metrics_logger_config.grouping_key)

    registry = CollectorRegistry()
    metrics = {
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }
    add_metrics(metrics)

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    gateway_metrics = r.json()['data'][0]
    for key in metrics:
        # Each metric is returned in a dictionary so we need to get the singular key
        # Assert value returned by gateway matches what we provided
        assert metrics[key] == float(
            gateway_metrics[key]['metrics'][0]['value'])
        assert 'GAUGE' == gateway_metrics[key]['type']

    # Clean up
    delete_from_gateway(metrics_logger_config.push_gateway, metrics_logger_config.id, grouping_key=metrics_logger_config.grouping_key)

def test_add_metrics_push_with_step():
    metrics_logger_config = MetricsLogger()
    delete_from_gateway(metrics_logger_config.push_gateway, metrics_logger_config.id, grouping_key=metrics_logger_config.grouping_key)

    print(requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics').json())
    registry = CollectorRegistry()
    metrics = {
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }
    add_metrics(metrics, step=0)

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    gateway_metrics = r.json()['data'][0]
    for key in metrics:
        # Each metric is returned in a dictionary so we need to get the singular key
        # Assert value returned by gateway matches what we provided
        assert metrics[key] == float(
            gateway_metrics[key]['metrics'][0]['value'])
        assert 'GAUGE' == gateway_metrics[key]['type']
        assert 'None' == gateway_metrics[key]['metrics'][0]['labels']['step']

    # Clean up
    delete_from_gateway(metrics_logger_config.push_gateway, metrics_logger_config.id, grouping_key=metrics_logger_config.grouping_key)

