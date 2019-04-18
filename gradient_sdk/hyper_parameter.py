from hyperopt import fmin, tpe
from hyperopt.mongoexp import MongoTrials
from pymongo.errors import ServerSelectionTimeoutError

from utils import get_mongo_conn_str, _experiment_name


def hyper_tune(train_model, hparam_def, algo=tpe.suggest, max_evals=25):
    """
    Function to prepare and run hyper parameter tune.

    :param train_model: User model to tune
    :param hparam_def: User hyper tune param definition
    :param algo: Search algorithm
    :param max_evals: Allow up to this many function evaluations before returning

    :return: None if there is no result or dict with result for tune
    """
    mongo_connect_str = get_mongo_conn_str()

    # TODO better handling of connection to mongo
    while True:
        try:
            trials = MongoTrials(mongo_connect_str, exp_key=_experiment_name())
        except ServerSelectionTimeoutError:
            pass
        else:
            return fmin(train_model, space=hparam_def, trials=trials, algo=algo, max_evals=max_evals)
