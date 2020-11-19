import mock
import pytest
import requests
import os

from gradient_utils.metrics import get_metric_pushgateway, CollectorRegistry
from gradient_utils.metrics import _add_metrics as add_metrics

LOCAL_PUSH_GATEWAY = os.getenv('PAPERSPACE_METRIC_PUSHGATEWAY')


def test_add_metrics_pushes_metrics():
    # Before tests, clear the push gateway
    # TODO: Run this before each
    requests.put(f'{LOCAL_PUSH_GATEWAY}/api/v1/admin/wipe')

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
