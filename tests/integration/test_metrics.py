import requests
import os
from prometheus_client import delete_from_gateway

from gradient_utils.metrics.metrics import MetricsLogger, add_metrics, _get_default_grouping_key
from gradient_utils.metrics.env import get_workload_id, get_metric_pushgateway

LOCAL_PUSH_GATEWAY = os.getenv('PAPERSPACE_METRIC_PUSHGATEWAY')


def clean_up_gateway(metric_names=None, steps=None):
    if metric_names is None:
        return
    if steps is None:
        steps = ["None"]
    for step in steps:
        for metric_name in metric_names:
            grouping_key = (_get_default_grouping_key())
            grouping_key.update({
                "name": metric_name,
                "step": step,
            })
            delete_from_gateway(
                get_metric_pushgateway(),
                get_workload_id(),
                grouping_key=grouping_key)


def test_add_metric_integration():
    m_logger = MetricsLogger()
    delete_from_gateway(
        m_logger._push_gateway,
        m_logger.id,
        grouping_key=m_logger._grouping_key)

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
        m_logger._push_gateway,
        m_logger.id,
        grouping_key=m_logger._grouping_key)


def test_add_metrics_pushes_metrics():
    metrics = {
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }
    add_metrics(metrics)

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    gateway_metrics = r.json()['data']
    for key in metrics:
        # Each metric is returned in a dictionary so we need to get the singular key
        # Assert value returned by gateway matches what we provided
        metric = None
        for m in gateway_metrics:
            if key in m:
                metric = m
                break
        assert metric
        assert metrics[key] == float(
            metric[key]['metrics'][0]['value'])
        assert 'GAUGE' == metric[key]['type']
        assert 'None' == metric[key]['metrics'][0]['labels']['step']

    # Clean up
    clean_up_gateway(['cat', 'dog', 'catdog'])


def test_add_metrics_push_with_step():
    metrics = {
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }
    add_metrics(metrics, step=0)

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    gateway_metrics = r.json()['data']
    for key in metrics:
        # Each metric is returned in a dictionary so we need to get the singular key
        # Assert value returned by gateway matches what we provided
        metric = None
        for m in gateway_metrics:
            if key in m:
                metric = m
                break
        assert metric
        assert metrics[key] == float(
            metric[key]['metrics'][0]['value'])
        assert 'GAUGE' == metric[key]['type']
        assert '0' == metric[key]['metrics'][0]['labels']['step']

    # Clean up
    clean_up_gateway(['cat', 'dog', 'catdog'], [0])


def test_add_metrics_multiple_steps():
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
            if key in inserted_metrics:
                step = inserted_metrics[key]['metrics'][0]['labels']['step']
                print(step)
                print(key)
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
    clean_up_gateway(["cat", "dog", "catdog"], [0, 1])


def test_add_metrics_overwrites_same_step():
    metrics = {
        'cat': 1,
        'dog': 2,
        'catdog': 1.2
    }
    add_metrics(metrics, step=0)
    add_metrics(metrics, step=0)

    # Get metrics
    r = requests.get(f'{LOCAL_PUSH_GATEWAY}/api/v1/metrics')
    # One row per metric are kept by the pushgateway
    assert 3 == len(r.json()['data'])

    # Clean up
    clean_up_gateway(['cat', 'dog', 'catdog'], [0])


def test_add_metrics_keeps_last_step():
    metrics_logger_config = MetricsLogger(step=0)
    delete_from_gateway(
        metrics_logger_config._push_gateway,
        metrics_logger_config.id,
        grouping_key=metrics_logger_config._grouping_key)

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

    gateway_metrics = r.json()['data']
    assert 4 == len(gateway_metrics)
    for metric in gateway_metrics:
        if "cat" in metric:
            assert '7' == metric['cat']['metrics'][0]['value']
        if "dog" in metric:
            assert '2' == metric['dog']['metrics'][0]['value']
        if "catdog" in metric:
            assert '1.2' == metric['catdog']['metrics'][0]['value']
        if "dragon" in metric:
            assert '23.5' == metric['dragon']['metrics'][0]['value']

    # Clean up
    clean_up_gateway(['cat', 'dog', 'catdog', 'dragon'], [0])
