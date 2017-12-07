from logging.handlers import RotatingFileHandler
from logstash import formatter


class FileLogstashHandler(RotatingFileHandler, object):
    """Python logging handler for Logstash. Save events to file.
    :param filename: Path to the log file.
    :param mode: File mode to write.
    :param maxBytes: Max file size before rotate.
    :param backupCount: Max number of backup log files.
    :param encoding: Encoding type.
    :param delay: Delay write log.
    :param message_type: The type of the message (default logstash).
    :param fqdn; Indicates whether to show fully qualified domain name or not (default False).
    :param version: version of logstash event schema (default is 0).
    :param tags: list of tags for a logger (default is None).
    """

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False, message_type='logstash', tags=None, fqdn=False, version=0):
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

        if version == 1:
            self.formatter = formatter.LogstashFormatterVersion1(message_type, tags, fqdn)
        else:
            self.formatter = formatter.LogstashFormatterVersion0(message_type, tags, fqdn)

    def makePickle(self, record):
        return self.formatter.format(record) + b'\n'
