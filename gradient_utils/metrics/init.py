from gradient_utils import metrics


def init(sync_tensorboard=False):
    if sync_tensorboard and len(metrics.patched["tensorboard"]) == 0:
        metrics.tensorboard.patch()
