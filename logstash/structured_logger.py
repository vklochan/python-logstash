__author__ = 'yigal'


class ArgsLogger:
    """
    A proxy convenience class used to make logging more structured.
    Example usage:

    logger = logging.getLogger("main_ELK")
    zmq_handler = ZmqLogstashHandler("ipc:///tmp/kinesis.socket")
    zmq_handler.setLevel(logging.INFO)
    logger.addHandler(zmq_handler)
    logger = ArgsLogger(logger)

    logger.info("NEW_BID", bid_price=2.3, bidder_id="1000", recommendation_mode="regular")

    :param _logger: The logger instance to proxy
    """
    def __init__(self, _logger):
        self.logger = _logger

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
