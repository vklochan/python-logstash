from logging import Handler
import socket
from logstash import formatter


# Derive from object to force a new-style class and thus allow super() to work
# on Python 2.6
class UnixLogstashHandler(Handler, object):
    """Python logging handler for Logstash. Sends events over Unix socket.
    :param socket_name: The name of the unix socket to use.
    """

    def __init__(self, socket_name, formatter_class=formatter.MiniLogstashFormatter, cpickle=False, **kwargs):
        """
        Initialize a handler.
        """
        Handler.__init__(self)

        self.formatter = formatter_class(**kwargs)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock.connect(socket_name)

    def emit(self, record):
        """
        Emit a record.
        """
        formatted_record = self.formatter.format(record) + b'\n'
        self.sock.sendall(formatted_record)

        return

    def __del__(self):
        try:
            self.sock.close()
        except:
            pass