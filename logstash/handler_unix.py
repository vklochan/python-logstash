from logging.handlers import SocketHandler
import socket
from logstash import formatter


# Derive from object to force a new-style class and thus allow super() to work
# on Python 2.6
class UnixLogstashHandler(SocketHandler, object):
    """Python logging handler for Logstash. Sends events over Unix socket.
    :param socket: The name of the unix socket to use.
    """

    def __init__(self, socket_name, port=5959, message_type='logstash', tags=None, fqdn=False, version=1):
        super(UnixLogstashHandler, self).__init__(socket_name, port)
        self.socketName = socket_name
        if version == 1:
            self.formatter = formatter.LogstashFormatterVersion1(message_type, tags, fqdn)
        else:
            self.formatter = formatter.LogstashFormatterVersion0(message_type, tags, fqdn)

    def makePickle(self, record):
        return self.formatter.format(record) + b'\n'

    def makeSocket(self, timeout=1):
        """
        A factory method which allows subclasses to define the precise
        type of socket they want.
        """
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if hasattr(s, 'settimeout'):
            s.settimeout(timeout)
        s.connect(self.socketName)
        return s