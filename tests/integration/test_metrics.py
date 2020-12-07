import mock
import pytest
import requests
import os
from prometheus_client import delete_from_gateway

from gradient_utils.metrics import get_metric_pushgateway, CollectorRegistry, add_metrics, MetricsLogger

LOCAL_PUSH_GATEWAY = os.getenv('PAPERSPACE_METRIC_PUSHGATEWAY')


def test_add_metric_integration():
    m_logger = MetricsLogger()
    delete_from_gateway(
        m_logger.push_gateway,
        m_logger.id,
        grouping_key=m_logger.grouping_key)

    m_logger.add_gauge("some_metric_1")
    m_logger.add_gauge("some_metric_2")
    m_logger["some_metric_1"].set(3)
    m_logger["some_metric_1"].inc()
    m_logger.push_metrics()

    expected = {
        "some_metric_1": '4',
        "some_metric_2": '0'
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
    delete_from_gateway(
        m_logger.push_gateway,
        m_logger.id,
        grouping_key=m_logger.grouping_key)


def test_add_metrics_pushes_metrics():
    # Before tests, clear the push gateway
    # TODO: Run this before each
    metrics_logger_config = MetricsLogger()
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)

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
        assert 'None' == gateway_metrics[key]['metrics'][0]['labels']['step']

    # Clean up
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)


def test_add_metrics_push_with_step():
    metrics_logger_config = MetricsLogger(step=0)
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)

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
        assert '0' == gateway_metrics[key]['metrics'][0]['labels']['step']

    # Clean up
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)


def test_add_metrics_multiple_steps():
    metrics_logger_config = MetricsLogger(step=0)
    metrics_logger_config_1 = MetricsLogger(step=1)
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)
    delete_from_gateway(
        metrics_logger_config_1.push_gateway,
        metrics_logger_config_1.id,
        grouping_key=metrics_logger_config_1.grouping_key)

    metrics = {
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }
    add_metrics(metrics, step=0)
    add_metrics(metrics, step=1)

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    gateway_metrics = r.json()['data']
    gateway_metrics_dict = {
        '0': {},
        '1': {}
    }
    for inserted_metrics in gateway_metrics:
        for key in metrics:
            step = inserted_metrics[key]['metrics'][0]['labels']['step']
            gateway_metrics_dict[step][key] = {}
            gateway_metrics_dict[step][key]['step'] = inserted_metrics[key]['metrics'][0]['labels']['step']
            gateway_metrics_dict[step][key]['value'] = inserted_metrics[key]['metrics'][0]['value']
            gateway_metrics_dict[step][key]['type'] = inserted_metrics[key]['type']

    # Step 0
    for key in metrics:
        assert metrics[key] == float(
            gateway_metrics_dict['0'][key]['value'])
        assert 'GAUGE' == gateway_metrics_dict['0'][key]['type']

    # Step 1
    for key in metrics:
        assert metrics[key] == float(
            gateway_metrics_dict['1'][key]['value'])
        assert 'GAUGE' == gateway_metrics_dict['1'][key]['type']

    # Clean up
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)
    delete_from_gateway(
        metrics_logger_config_1.push_gateway,
        metrics_logger_config_1.id,
        grouping_key=metrics_logger_config_1.grouping_key)


def test_add_metrics_aggregrates_same_step():
    metrics_logger_config = MetricsLogger(step=0)
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)

    metrics = {
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }
    add_metrics(metrics, step=0)
    add_metrics(metrics, step=0)

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    # One row of metrics are aggregrated by the pushgateway
    assert 1 == len(r.json()['data'])

    # Clean up
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)


def test_add_metrics_keeps_last_step():
    metrics_logger_config = MetricsLogger(step=0)
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)

    add_metrics({
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }, step=0)
    add_metrics({
        'cat': 1,
        'dragon': 23.5
    }, step=0)
    add_metrics({
        'cat': 7,
    }, step=0)

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    # One row of metrics are aggregrated by the pushgateway

    assert '7' == r.json()['data'][0]['cat']['metrics'][0]['value']
    assert 'dragon' not in r.json()['data'][0]
    assert 'catdog' not in r.json()['data'][0]
    assert 'dog' not in r.json()['data'][0]

    # Clean up
    delete_from_gateway(
        metrics_logger_config.push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config.grouping_key)
