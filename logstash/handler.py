from logging.handlers import DatagramHandler
from logstash import formatter


class LogstashHandler(DatagramHandler):
    """Python logging handler for Logstash
    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 5959).
    :param message_type: The type of the message (default logstash).
    :param fqdn; Indicates whether to show fully qualified domain name or not (default False).
    :param version: version of logstash event schema (default is 0).
    """

    def __init__(self, host, port=5959, message_type='logstash', fqdn=False, version=0):
        DatagramHandler.__init__(self, host, port)
        if version == 1:
            self.formatter = formatter.LogstashFormatterVersion1(message_type, [], fqdn)
        else:
            self.formatter = formatter.LogstashFormatterVersion0(message_type, [], fqdn)

    def makePickle(self, record):
        return self.formatter.format(record)
