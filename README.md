![GitHubSplash](https://user-images.githubusercontent.com/585865/65443342-e630d300-ddfb-11e9-9bcd-de1d2033ea60.png)

# Gradient Utils

![PyPI](https://img.shields.io/pypi/v/gradient-utils)
[![codecov](https://codecov.io/gh/Paperspace/gradient-utils/branch/master/graph/badge.svg)](https://codecov.io/gh/Paperspace/gradient-utils)

<br>

**Get started:** [Create Account](https://www.paperspace.com/account/signup?gradient=true) • [Install CLI](https://docs.paperspace.com/gradient/get-started/install-the-cli) • [Tutorials](https://docs.paperspace.com/gradient/tutorials) • [Docs](https://docs.paperspace.com/gradient)

**Resources:** [Website](https://gradient.paperspace.com/) • [Blog](https://blog.paperspace.com/) • [Support](https://support.paperspace.com/hc/en-us) • [Contact Sales](https://use.paperspace.com/contact-sales)

<br>

Gradient is an an end-to-end MLOps platform that enables individuals and organizations to quickly develop, train, and deploy Deep Learning models. The Gradient software stack runs on any infrastructure e.g. AWS, GCP, on-premise and low-cost [Paperspace GPUs](https://gradient.paperspace.com/instances). Leverage automatic versioning, distributed training, built-in graphs & metrics, hyperparameter search, GradientCI, 1-click Jupyter Notebooks, our Python SDK, and more.

This is an SDK for performing Machine Learning with Gradientº, it can be installed in addition to [gradient-cli](https://github.com/Paperspace/gradient-cli).

# Requirements

This SDK requires Python 3.6+.

To install it, run:

```bash
pip install gradient-utils
```

# Usage

## Metrics

Library for logging custom and framework metrics in Gradient.

Usage example:

```python
from gradient_utils.metrics import init, add_metrics, MetricsLogger

# Initialize metrics logging
with init():
    # do work here
    pass

# Capture metrics produced by tensorboard
with init(sync_tensorboard=True):
    # do work here
    pass

# Log metrics with a single command
add_metrics({"loss": 0.25, "accuracy": 0.99})

# Insert metrics with a step value
# Note: add_metrics should be called once for a step.
#       Multiple calls with the same step may result in loss of metrics.
add_metrics({"loss": 0.25, "accuracy": 0.99}, step=0)

# For more advanced use cases use the MetricsLogger
logger = MetricsLogger()
logger.add_gauge("loss") # add a specific gauge
logger["loss"].set(0.25)
logger["loss"].inc()
logger.add_gauge("accuracy")
logger["accuracy"].set(0.99)
logger.push_metrics() # you must explicitly push metrics each time you mutate values when using MetricsLogger

# You can also use steps with the MetricsLogger
logger = MetricsLogger(step=0)
logger.add_gauge("loss")
logger["loss"].set(0.25)
logger.push_metrics()
logger.set_step(1) # update step explicitly
logger["loss"].set(0.25)
logger.push_metrics()
```

## Multinode Helper Functions

### Multinode GRPC Tensorflow

**Set the TF_CONFIG environment variable**
For multi-worker training, you need to set the `TF_CONFIG` environment variable for each binary running in your cluster. Set the value of `TF_CONFIG` to a JSON string that specifies each task within the cluster, including each task's address and role within the cluster. We've provided a Kubernetes template in the tensorflow/ecosystem repo which sets `TF_CONFIG` for your training tasks.

**get_tf_config()**

Function to set value of `TF_CONFIG` when run on machines within Paperspace infrastructure.

It can raise a `ConfigError` exception with message if there's a problem with its configuration in a particular machine.

**_Usage example:_**

```python
from gradient_utils import get_tf_config

get_tf_config()
```

## Utility Functions

**get_mongo_conn_str()**

Function to check and construct MongoDB connection string.

It returns a connection string to MongoDB.

It can raise a `ConfigError` exception with message if there's a problem with any values used to prepare the MongoDB connection string.

Usage example:

```python
from gradient_utils import get_mongo_conn_str

conn_str = get_mongo_conn_str()
```

**data_dir()**

Function to retrieve path to job space.

Usage example:

```python
from gradient_utils import data_dir

job_space = data_dir()
```

**model_dir()**

Function to retrieve path to model space.

Usage example:

```python
from gradient_utils import model_dir

model_path = model_dir(model_name)
```

**export_dir()**

Function to retrieve path for model export.

Usage example:

```python
from gradient_utils import export_dir

model_path = export_dir(model_name)
```

**worker_hosts()**

Function to retrieve information about worker hosts.

Usage example:

```python
from gradient_utils import worker_hosts

model_path = worker_hosts()
```

**ps_hosts()**

Function to retrieve information about Paperspace hosts.

Usage example:

```python
from gradient_utils import ps_hosts

model_path = ps_hosts()
```

**task_index()**

Function to retrieve information about task index.

Usage example:

```python
from gradient_utils import task_index

model_path = task_index()
```

**job_name()**

Function to retrieve information about job name.

Usage example:

```python
from gradient_utils import job_name

model_path = job_name()
```

# Contributing

## Setup

We use Docker and Docker-compose to run the tests locally.

```
# To setup the integration test framework
docker-compose up --remove-orphans -d pushgateway
docker-compose build utils

# To run tests
docker-compose -f docker-compose.ci.yml run utils poetry run pytest

# To autoformat
docker-compose run utils poetry run autopep8 --in-place --aggressive --aggressive --recursive .
```
