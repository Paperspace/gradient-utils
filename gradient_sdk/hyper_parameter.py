import logging
import os
from time import sleep

from hyperopt import fmin, tpe
from hyperopt.mongoexp import MongoTrials
from pymongo.errors import ServerSelectionTimeoutError

from gradient_sdk.utils import get_mongo_conn_str, _experiment_name, _check_mongo_client_connection

logger = logging.getLogger(__name__)


def _hyper_tune_check():
    """
    Function to check all requirements for hyper tune

    :return: bool value when all check complete
    """
    max_retry = os.environ.get("MAX_CONNECTION_RETRY", 5)
    retry_timeout = os.environ.get("CONNECTION_RETRY_TIMEOUT", 5)

    is_check_complete = False

    for i in range(max_retry):
        logger.warning("Hyper Tune Check - check connection to mongo db")
        is_connection_available = _check_mongo_client_connection()

        if not is_connection_available:
            current_retry_timeout = (i + 1) * retry_timeout
            logger.warning(
                "Hyper Tune Check - connection is not available retry next connection check in %s seconds",
                current_retry_timeout
            )
            sleep(current_retry_timeout)
        else:
            is_check_complete = True
            break

    return is_check_complete


def hyper_tune(train_model, hparam_def, algo=tpe.suggest, max_evals=25, func=fmin):
    """
    Function to prepare and run hyper parameter tune.

    :param train_model: User model to tune
    :param hparam_def: User hyper tune param definition
    :param algo: Search algorithm
    :param max_evals: Allow up to this many function evaluations before returning
    :param func: function that will run hyper tune logic, by default hyperopt fmin function

    :return: None if there is no result or dict with result for tune
    """
    mongo_connect_str = get_mongo_conn_str()
    is_connection_available = True

    while is_connection_available:
        try:
            trials = MongoTrials(mongo_connect_str, exp_key=_experiment_name())
        except ServerSelectionTimeoutError:
            logger.warning("Hyper Tune - MongoTrials server selection Timeout Error")
            is_connection_available = _hyper_tune_check()
        else:
            return func(train_model, space=hparam_def, trials=trials, algo=algo, max_evals=max_evals)
