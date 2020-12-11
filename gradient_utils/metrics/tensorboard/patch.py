import sys
import logging
import threading
import time
import socket
import os
from importlib import import_module, reload
from gradient_utils import metrics

reload(logging)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%I:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
TENSORBOARD_C_MODULE = "tensorboard.python.ops.gen_summary_ops"
TENSORBOARD_WRITER_MODULE = "tensorboard.summary.writer.event_file_writer"
TENSORBOARDX_WRITER_MODULE = "tensorboardX.event_file_writer"
TENSORBOARD_PYTORCH_MODULE = "torch.utils.tensorboard.writer"


def patch(settings=None):
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
        _patch_tensorboard(writer=c, module=TENSORBOARD_C_MODULE, settings=settings)
    if tb:
        _patch_tensorboardx(writer=tb, module=TENSORBOARD_WRITER_MODULE, settings=settings)
    if tbx:
        _patch_tensorboardx(writer=tbx, module=TENSORBOARDX_WRITER_MODULE, settings=settings)
        del sys.modules["tensorboardX"]
        del sys.modules["tensorboardX.writer"]
    if pt:
        _patch_tensorboardx(writer=pt, module=TENSORBOARD_PYTORCH_MODULE, settings=settings)
        # uncaching pytorch crashes in user code due to imoprt side effects


def _get_module(name, required=False):
    try:
        return import_module(name)
    except Exception as e:
        if required:
            raise ValueError(
                "Error importing module '{name}'.".format(name=name)
            )


def _patch_tensorboard(writer, module, settings):
    prev_func = writer.create_summary_file_writer

    def new_func(*args, **kwargs):
        logger.debug("new_func")
        logdir = (
            kwargs["logdir"].numpy().decode("utf8")
            if hasattr(kwargs["logdir"], "numpy")
            else kwargs["logdir"]
        )
        on_new_logdir(logdir, settings)
        return prev_func(*args, **kwargs)

    writer.prev_create_summary_file_writer = prev_func
    writer.create_summary_file_writer = new_func
    metrics.patched["tensorboard"].append([module, "create_summary_file_writer"])
    logger.debug("patching %s.%s", module, "create_summary_file_writer")


def _patch_tensorboardx(writer, module, settings):
    prev_class = writer.EventFileWriter

    class TBXWriter(prev_class):
        def __init__(self, *args, **kwargs):
            logdir = kwargs.pop("logdir", None)
            if logdir is None:
                logdir = args[0]
            on_new_logdir(logdir, settings)
            super(TBXWriter, self).__init__(*args, **kwargs)

    writer.prev_EventFileWriter = prev_class
    writer.EventFileWriter = TBXWriter
    metrics.patched["tensorboard"].append([module, "EventFileWriter"])
    logger.debug("patching %s.%s", module, "EventFileWriter")


def on_new_logdir(logdir, settings):
    logger.debug("Watching %s", logdir)
    watcher = LogdirWatcher(logdir, settings)
    watcher.start()


class LogdirWatcher(object):
    def __init__(self, logdir, settings):
        self._logdir = logdir
        self._settings = settings
        self._hostname = socket.gethostname()
        self.event_file_loader = _get_module("tensorboard.backend.event_processing.event_file_loader", required=True)
        self.directory_watcher = _get_module("tensorboard.backend.event_processing.directory_watcher", required=True)
        self.tf_compat = _get_module("tensorboard.compat", required=True)
        self._generator = self.directory_watcher.DirectoryWatcher(logdir, self.event_file_loader.EventFileLoader,
                                                                  self._is_new_tfevents_file)
        self._thread = threading.Thread(target=self._thread_body)

    def start(self):
        self._thread.start()

    def _thread_body(self):
        logger.debug("_thread_body")
        while True:
            time.sleep(1)
            try:
                for event in self._generator.Load():
                    self._process_event(event)
            except self.directory_watcher.DirectoryDeletedError:
                logger.debug("directory deleted")
                break

    def _process_event(self, event):
        if event.HasField("summary"):
            try:
                step = event.step
                summary = event.summary
                for value in summary.value:
                    name = value.tag.replace(".", "_").replace("/", "_").replace(" ", "_")
                    metric = get_metric_from_summary(value)
                    if metric:
                        logger.debug("adding metric %s with value %s", name, metric)
                        metrics.add_metrics({name: metric}, step=step)
                    else:
                        logger.debug("no metric found for %s", name)
            except Exception as e:
                logger.debug("%s", e)

    def _is_new_tfevents_file(self, path=""):
        path = self.tf_compat.tf.compat.as_str_any(path)
        return is_new_tfevents_file(
            path, self._hostname, self._settings.start_time
        )


def is_new_tfevents_file(path, hostname, start_time):
    if path == "":
        raise ValueError("Path must be a nonempty string")

    # check the filename
    basename = os.path.basename(path)
    if basename.endswith(".profile-empty"):
        return False
    fname_components = basename.split(".")
    try:
        tfevents_idx = fname_components.index("tfevents")
    except ValueError:
        return False

    # check the hostname, which may have dots
    for i, part in enumerate(hostname.split(".")):
        try:
            fname_component_part = fname_components[tfevents_idx + 2 + i]
        except IndexError:
            return False
        if part != fname_component_part:
            return False

    # check the create time
    try:
        created_time = int(fname_components[tfevents_idx + 1])
    except (ValueError, IndexError):
        return False
    return created_time >= start_time


def get_metric_from_summary(value):
    if value.simple_value:
        return value.simple_value
    if value.HasField("tensor"):
        tensor = value.tensor
        if tensor.tensor_content:
            # TODO marshal tensor_content
            logger.debug("exiting tensor_content")
            return None
        logger.debug(tensor.dtype)
        if tensor.dtype == 1:
            logger.debug(tensor)
            if tensor.float_val:
                return tensor.float_val[0]
        if tensor.dtype == 2 and tensor.double_val:
            return tensor.double_val[0]
        if tensor.dtype in [3, 4, 5, 6] and tensor.int_val:
            return tensor.int_val[0]
        if tensor.dtype == 19 and tensor.half_val:
            return tensor.half_val[0]
        if tensor.dtype == 9 and tensor.int64_val:
            return tensor.int64_val[0]
    return None
