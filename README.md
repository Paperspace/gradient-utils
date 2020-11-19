![GitHubSplash](https://user-images.githubusercontent.com/585865/65443342-e630d300-ddfb-11e9-9bcd-de1d2033ea60.png)

Gradient Utils
=================

![PyPI](https://img.shields.io/pypi/v/gradient-utils)
[![codecov](https://codecov.io/gh/Paperspace/gradient-utils/branch/master/graph/badge.svg)](https://codecov.io/gh/Paperspace/gradient-utils)

<br>

**Get started:** [Create Account](https://www.paperspace.com/account/signup?gradient=true) • [Install CLI](https://docs.paperspace.com/gradient/get-started/install-the-cli) • [Tutorials](https://docs.paperspace.com/gradient/tutorials) • [Docs](https://docs.paperspace.com/gradient)

**Resources:** [Website](https://gradient.paperspace.com/) • [Blog](https://blog.paperspace.com/) • [Support](https://support.paperspace.com/hc/en-us) • [Contact Sales](https://use.paperspace.com/contact-sales)

<br>

Gradient is an an end-to-end MLOps platform that enables individuals and organizations to quickly develop, train, and deploy Deep Learning models.  The Gradient software stack runs on any infrastructure e.g. AWS, GCP, on-premise and low-cost [Paperspace GPUs](https://gradient.paperspace.com/instances).  Leverage automatic versioning, distributed training, built-in graphs & metrics, hyperparameter search, GradientCI, 1-click Jupyter Notebooks, our Python SDK, and more. 

This is an SDK for performing Machine Learning with Gradientº, it can be installed in addition to [gradient-cli](https://github.com/Paperspace/gradient-cli).

# Requirements

This SDK requires Python 3.5+.

To install it, run:

```bash
pip install gradient-utils
```

# Usage

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

## Hyperparameter Tuning

Currently, Gradientº only supports _Hyperopt_ for Hyperparameter Tuning.

**hyper_tune()**

Function to run hyperparameter tuning.

It accepts the following arguments:

- `train_model`
  User model to tune.
- `hparam_def`
  User definition (scope) of search space.
  To set this value, refer to [hyperopt documentation](https://github.com/hyperopt/hyperopt).
- `algo`
  Search algorithm.
  _Default_: `tpe.suggest` (from hyperopt).
- `max_ecals`
  Maximum number of function evaluations to allow before returning.
  _Default_: `25`.
- `func`
  Function to be run by hyper tune.
  _Default_: `fmin` (from hyperopt). _Do not change this value if you do not know what you are doing!_

It returns a dict with information about the tuning process.

It can raise a `ConfigError` exception with message if there's no connection to MongoDB.

**Note:** _You do not need to worry about setting your MongoDB version; it will be set within Paperspace infrastructure for hyperparameter tuning._

**Usage example:**

```python
from gradient_utils import hyper_tune

# Prepare model and search scope

# minimal version
argmin1 = hyper_tune(model, scope)

# pass more arguments
argmin2 = hyper_tune(model, scope, algo=tpe.suggest, max_evals=100)
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

## Metrics
Prometheus wrapper for logging custom metrics

Usage example:

```python
from gradient_utils import MetricsLogger
# Comment: add_metrics is not supported at the moment. Stay tuned!
# from gradient_utils.metrics import add_metrics
m_logger = MetricsLogger()
m_logger.add_gauge("some_metric_1")
m_logger["some_metric_1"].set(3)
m_logger["some_metric_1"].inc()

m_logger.add_gauge("some_metric_2")
m_logger["some_metric_2"].set_to_current_time()

m_logger.push_metrics()

# Insert metrics with a single command
# add_metrics({
#   'loss': 0.25,
#   'accuracy': 0.99
# })

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
```

