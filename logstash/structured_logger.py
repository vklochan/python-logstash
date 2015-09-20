import formatter
import logging
from logstash import ZmqLogstashHandler, UnixLogstashHandler

__author__ = 'yigal'


class ArgsLogger:
    """
    A proxy convenience class used to make logging more structured.
    Example usages:

    (1) To let the class construct a logger with default parameters, simply:

        logger = ArgsLogger("zmq")

    (2) To set the 'module' field used by the formatter:

        logger = ArgsLogger("zmq", module="MyGreatModule", server_type="MyServer")

    (3) To make the handler communicate on a different address:

        logger = ArgsLogger("zmq", ["tcp://my.receiver.addr:5555"], module="MyGreatModule")

    (4) To customize the parameters and classes used, pass a ready logger which will be proxied:

        logger = logging.getLogger("main_ELK")
        zmq_handler = ZmqLogstashHandler("ipc:///tmp/kinesis.socket")
        logger.setLevel(logging.INFO)
        logger.addHandler(zmq_handler)
        logger = ArgsLogger(logger)

        logger.info("NEW_BID", bid_price=2.3, bidder_id="1000", recommendation_mode="regular")

    :param logger_type: The type of communication to use ("zmq"|"unix"), or the logger instance to proxy
    :param logger_pos_params: Optional list of positional arguments to pass the handler's constructor
    """
    STR_TO_TYPE = dict(zmq=ZmqLogstashHandler, unix=UnixLogstashHandler)
    STR_TO_ADDR = dict(zmq="ipc:///tmp/logstash.socket", unix="/tmp/logstash.socket")

    def __init__(self, logger_type, logger_pos_params=None, **kwargs):
        if isinstance(logger_type, basestring):
            logger_kw_params = kwargs
            logger_kw_params.update(dict(formatter_class=formatter.AWSLogstashFormatter))
            if logger_pos_params is None:
                logger_pos_params = [self.STR_TO_ADDR[logger_type]]
            self.logger = logging.getLogger("ELK")
            handler = self.STR_TO_TYPE[logger_type](*logger_pos_params, **logger_kw_params)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = logger_type

    def debug(self, event_type, **kwargs):
        self.logger.debug(event_type, extra=kwargs)

    def info(self, event_type, **kwargs):
        self.logger.info(event_type, extra=kwargs)

    def warning(self, event_type, **kwargs):
        self.logger.warning(event_type, extra=kwargs)

    def exception(self, event_type, **kwargs):
        self.logger.exception(event_type, extra=kwargs)

    def error(self, event_type, **kwargs):
        self.logger.error(event_type, extra=kwargs)
