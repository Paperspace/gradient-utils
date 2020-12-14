import sys
import logging
from importlib import import_module, reload
from gradient_utils import metrics

logger = logging.getLogger(__name__)
TENSORBOARD_C_MODULE = "tensorboard.python.ops.gen_summary_ops"
TENSORBOARD_WRITER_MODULE = "tensorboard.summary.writer.event_file_writer"
TENSORBOARDX_WRITER_MODULE = "tensorboardX.event_file_writer"
TENSORBOARD_PYTORCH_MODULE = "torch.utils.tensorboard.writer"


def patch():
    if len(metrics.patched["tensorboard"]) > 0:
        raise ValueError(
            "Tensorboard already patched. You may be calling metrics.init() more than once."
        )

    # Make sure tensorboard is installed
    _get_module("tensorboard", required=True)

    # Grab specific tensorboard modules for patching
    c = _get_module(TENSORBOARD_C_MODULE)
    tb = _get_module(TENSORBOARD_WRITER_MODULE)
    tbx = _get_module(TENSORBOARDX_WRITER_MODULE)
    pt = _get_module(TENSORBOARD_PYTORCH_MODULE)

    if not c and not tb and not pt:
        raise ValueError(
            "Could not find a valid tensorboard module to patch"
        )

    patched = []
    if c:
        _patch_tensorboard(writer=c, module=TENSORBOARD_C_MODULE)
        patched.append(TENSORBOARD_C_MODULE)
    if tb:
        _patch_tensorboardx(writer=tb, module=TENSORBOARD_WRITER_MODULE)
        patched.append(TENSORBOARD_WRITER_MODULE)
    if tbx:
        _patch_tensorboardx(writer=tbx, module=TENSORBOARDX_WRITER_MODULE)
        patched.append(TENSORBOARDX_WRITER_MODULE)
        del sys.modules["tensorboardX"]
        del sys.modules["tensorboardX.writer"]
    if pt:
        _patch_tensorboardx(writer=pt, module=TENSORBOARD_PYTORCH_MODULE)
        # uncaching pytorch crashes in user code due to imoprt side effects


def _get_module(name, required=False):
    try:
        return import_module(name)
    except Exception as e:
        if required:
            raise ValueError(
                "Error importing module '{name}'.".format(name=name)
            )


def _patch_tensorboard(writer, module):
    prev_func = writer.create_summary_file_writer

    def new_func(*args, **kwargs):
        logger.debug("new_func")
        logdir = (
            kwargs["logdir"].numpy().decode("utf8")
            if hasattr(kwargs["logdir"], "numpy")
            else kwargs["logdir"]
        )
        on_new_logdir(logdir)
        return prev_func(*args, **kwargs)

    writer.prev_create_summary_file_writer = prev_func
    writer.create_summary_file_writer = new_func
    metrics.patched["tensorboard"].append([module, "create_summary_file_writer"])
    logger.debug("patching %s.%s", module, "create_summary_file_writer")


def _patch_tensorboardx(writer, module):
    prev_class = writer.EventFileWriter

    class TBXWriter(prev_class):
        def __init__(self, *args, **kwargs):
            logdir = kwargs.pop("logdir", None)
            if logdir is None:
                logdir = args[0]
            on_new_logdir(logdir)
            super(TBXWriter, self).__init__(*args, **kwargs)

    writer.prev_EventFileWriter = prev_class
    writer.EventFileWriter = TBXWriter
    metrics.patched["tensorboard"].append([module, "EventFileWriter"])
    logger.debug("patching %s.%s", module, "EventFileWriter")


def on_new_logdir(logdir):
    logger.debug(logdir)
