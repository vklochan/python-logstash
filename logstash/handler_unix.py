from logging import Handler
import socket
from logstash import formatter


# Derive from object to force a new-style class and thus allow super() to work
# on Python 2.6
class UnixLogstashHandler(Handler, object):
    """Python logging handler for Logstash. Sends events over Unix socket.
    :param socket_name: The name of the unix socket to use.
    """

    def __init__(self, socket_name, formatter_class=formatter.MiniLogstashFormatter, **kwargs):
        """
        Initialize a handler.
        """
        Handler.__init__(self)

        self.formatter = formatter_class(**kwargs)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(socket_name)

    def emit(self, record):
        """
        Emit a record.
        """
        try:
            formatted_record = self.formatter.format(record)
            self.sock.sendall(formatted_record + b'\n')
        except socket.error:
            self.sock.close()