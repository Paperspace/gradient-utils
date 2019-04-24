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

## 1. Multinode

For now we only support TensorFlow.

**get_tf_config()**

Prepare `TF_CONFIG` variable.

Example of usage:
```python
from gradient_sdk import get_tf_config

get_tf_config()
```

This function will set `TF_CONFIG` when run on machines in Paperspace infrastructure.
If there would be any problem with configuration of this environment variable in machines then will be raised `ConfigError` with message.

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
