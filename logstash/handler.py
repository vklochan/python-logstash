import traceback
import socket
from logging.handlers import DatagramHandler
from message import LogstashMessage, LogstashMessageVersion0


class LogstashHandler(DatagramHandler):
    """Python logging handler for Logstash
    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 5959).
    :param message_type: The type of the message (default logstash).
    :param fqdn; Indicates whether to show fully qualified domain name or not (default False).
    :param version: version of logstash event schema (default is 0).
    """

    def __init__(self, host, port=5959, message_type='logstash', fqdn=False, version=0):
        self.message_type = message_type
        self.fqdn = fqdn
        self.version = version
        DatagramHandler.__init__(self, host, port)

    def makePickle(self, record):
        message = self.build_message(record)
        return message.get_json()

    def build_message(self, record):
        add_debug_info = False

        if self.fqdn:
            host = socket.getfqdn()
        else:
            host = socket.gethostname()

        # if version is not specified use version 0
        logstashMessageType = LogstashMessage if self.version == 1 else LogstashMessageVersion0
        # create message object
        message = logstashMessageType(record.getMessage(), host, record.pathname, [], record.created, self.message_type, record.levelname, record.name)

        # if exception, add debug info
        if record.exc_info:
            add_debug_info = True
            message.setExtraField('exc_info', self.format_exception(record.exc_info))

        if add_debug_info:
            message.setExtraField('lineno', record.lineno)
            message.setExtraField('process', record.process)
            message.setExtraField('threadName', record.threadName)
            # funName was added in 2.5
            if not getattr(record, 'funcName', None):
                message.setExtraField('funcName', record.funcName)
            # processName was added in 2.6
            if not getattr(record, 'processName', None):
                message.setExtraField('processName', record.processName)

        message = self.add_extra_fields(message, record)

        return message

    def add_extra_fields(self, message, record):
        # The list contains all the attributes listed in
        # http://docs.python.org/library/logging.html#logrecord-attributes
        skip_list = (
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName')

        for key, value in record.__dict__.items():
            if key not in skip_list:
                if isinstance(value, (basestring, bool, dict, float, int, list, type(None))):
                    message.setExtraField(key, value)
                else:
                    message.setExtraField(key, repr(value))

        return message

    def format_exception(self, exc_info):
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''
