# Gradient ML SDK

This is SDK to work with Paperspace infrastructure.

**Remember:**
For now this SDK is not prepared to work on machines outside of Paperspace infrastructure!

# Requirements

This SDK works with Python 3.5+ version.

You can install it with:

```bash
pip install gradient-sdk
```

# How to use it

## Multinode Helper functions

### Multinode GRPC Tensorflow

Setting up TF_CONFIG environment variable
For multi-worker training, as mentioned before, you need to us set "TF_CONFIG" environment variable for each binary running in your cluster. The "TF_CONFIG" environment variable is a JSON string which specifies what tasks constitute a cluster, their addresses and each task's role in the cluster. We provide a Kubernetes template in the tensorflow/ecosystem repo which sets "TF_CONFIG" for your training tasks.

**get_tf_config()**

This function will set `TF_CONFIG` when run on machines in Paperspace infrastructure.
If there would be any problem with configuration of this environment variable in machines then will be raised `ConfigError` with message.

Example of usage:
```python
from gradient_sdk import get_tf_config

get_tf_config()
```

## Hyper Tune

For now we only support Hyperopt

 **hyper_tune**
 
 Function that run hyper tune. This function accept arguments:
 - `train_model`
 User model to tune
 - `hparam_def`
 User definition (scope) of search space.
 To set this value you can look at hyperopt documentation.
 - `algo` 
 Search algorithm.
 Default set to `tpe.suggest` from hyperopt
 - `max_ecals` 
 Allow up to this many function evaluations before returning. 
 Default set to 25.
 - `func` 
 Function that will run hyper tune.
 Default set to `fmin` from hyperopt. _Do not change it if you do not know what you are doing_
 
This function return dict with information about tune process.
It also can raise `ConfigError` exception where there is no connection to mongo db.
_You do not need to worry about setting your version of mongo db because it will be set in Paperspace infrastructure for hyper parameter tune._
 
Example of usage:
```python
from gradient_sdk import hyper_tune

# Prepare model and search scope

# minimal version
argmin1 = hyper_tune(model, scope)

# pass more arguments
argmin2 = hyper_tune(model, scope, algo=tpe.suggest, max_evals=100)
```
 
 ## Utility functions

**get_mongo_conn_str**

Function to check and construct mongo db connection string.

If there are some problems with values to prepare connection string to mongo db there is raised `ConfigError` with message.

It will return connection string to mongo db.

Example of usage:
```python
from gradient_sdk import get_mongo_conn_str

conn_str = get_mongo_conn_str()
```

**data_dir**

Function to retrieve path to job space.

Example of usage:
```python
from gradient_sdk import data_dir

job_space = data_dir()
```

**model_dir**

Function to retrieve path to model space.

Example of usage:
```python
from gradient_sdk import model_dir

model_path = model_dir(model_name)
```

**export_dir**

Function to retrieve path for model export.

Example of usage:
```python
from gradient_sdk import export_dir

model_path = export_dir(model_name)
```

**worker_hosts**

Function to retrieve information about worker hosts.

Example of usage:
```python
from gradient_sdk import worker_hosts

model_path = worker_hosts()
```

**ps_hosts**

Function to retrieve information about paperspace hosts.

Example of usage:
```python
from gradient_sdk import ps_hosts

model_path = ps_hosts()
```

**task_index**

Function to retrieve information about task index.

Example of usage:
```python
from gradient_sdk import task_index

model_path = task_index()
```

**job_name**

Function to retrieve information about job name.

Example of usage:
```python
from gradient_sdk import job_name

model_path = job_name()
```
