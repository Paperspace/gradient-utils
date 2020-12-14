import os

PUSH_GATEWAY_ENV = 'PAPERSPACE_METRIC_PUSHGATEWAY'
PUSH_GATEWAY_DEFAULT = 'http://gradient-processing-prometheus-pushgateway:9091'
WORKLOAD_TYPE_ENV = 'PAPERSPACE_METRIC_WORKLOAD_TYPE'
WORKLOAD_TYPE_DEFAULT = 'experiment'
WORKLOAD_ID_ENV = 'PAPERSPACE_METRIC_WORKLOAD_ID'
LEGACY_EXPERIMENT_ID_ENV = 'PAPERSPACE_EXPERIMENT_ID'
HOSTNAME = os.getenv("HOSTNAME")


def get_metric_pushgateway():
    return os.getenv(PUSH_GATEWAY_ENV, PUSH_GATEWAY_DEFAULT)


def get_workload_type():
    return os.getenv(WORKLOAD_TYPE_ENV, WORKLOAD_TYPE_DEFAULT)


def get_workload_label():
    return 'label_metrics_{}_handle'.format(get_workload_type())


def _get_env_var_or_raise(*env_vars):
    rv = None
    for env_var in env_vars:
        rv = os.getenv(env_var)
        if not rv:
            break

    if rv is None:
        msg = "{} environment variable(s) not found".format(
            ", ".join(env_vars))
        raise ValueError(msg)

    return rv


def _get_experiment_id():
    if os.getenv(LEGACY_EXPERIMENT_ID_ENV):
        return os.getenv(LEGACY_EXPERIMENT_ID_ENV)
    try:
        experiment_id = HOSTNAME.split('-')[1]
        return experiment_id
    except IndexError:
        msg = "Experiment ID not found"
        raise ValueError(msg)


def get_workload_id():
    if os.getenv(WORKLOAD_ID_ENV):
        return os.getenv(WORKLOAD_ID_ENV)
    return _get_experiment_id()

