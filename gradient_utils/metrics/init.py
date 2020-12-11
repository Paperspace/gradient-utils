import time
from gradient_utils import metrics


class Settings(object):
    start_time = None


def init(sync_tensorboard=False):
    settings = Settings()
    settings.start_time = time.time()
    if sync_tensorboard and len(metrics.patched["tensorboard"]) == 0:
        metrics.tensorboard.patch(settings)
