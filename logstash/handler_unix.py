from logging import Handler
import socket
from logstash import formatter


# Derive from object to force a new-style class and thus allow super() to work
# on Python 2.6
class UnixLogstashHandler(Handler, object):
    """Python logging handler for Logstash. Sends events over Unix socket.
    :param socket_name: The name of the unix socket to use.
    """

    def __init__(self, socket_name, message_type='logstash', tags=None, fqdn=False):
        """
        Initialize a handler.
        """
        Handler.__init__(self)

        self.formatter = formatter.LogstashFormatterVersion1(message_type, tags, fqdn)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(socket_name)

    def emit(self, record):
        """
        Emit a record.
        """
        self.sock.sendall(self.formatter.format(record) + b'\n')