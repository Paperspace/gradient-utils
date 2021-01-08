import time
from gradient_utils import metrics


class Settings(object):
    start_time = None
    tensorboard_watchers = []


class Init(object):
    def __init__(self):
        self._settings = Settings()

    def init(self, sync_tensorboard):
        self._settings.start_time = time.time()
        if sync_tensorboard and len(metrics.patched["tensorboard"]) == 0:
            metrics.tensorboard.patch(self._settings)

    def finish(self):
        for watcher in self._settings.tensorboard_watchers:
            watcher.finish()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()
        return exc_type is None


def init(sync_tensorboard=False):
    i = Init()
    i.init(sync_tensorboard=sync_tensorboard)
    return i
