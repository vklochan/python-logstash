from logging import Handler
import random
import socket
import time
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
        self.sock.settimeout(2)
        self.sock.connect(socket_name)
        self.socket_name = socket_name

    def emit(self, record):
        """
        Emit a record.
        """
        formatted_record = self.formatter.format(record) + b'\n'

        backoff_time = 0.001
        sent = False
        while not sent:
            try:
                self.sock.sendall(formatted_record)
                sent = True
            except socket.error:
                pass
            except IOError:
                pass

            if not sent:
                self.sock.close()
                time.sleep(backoff_time)
                backoff_time *= (1.5 + 1 * random.random())

                try:
                    self.sock.connect(self.socket_name)
                except IOError:
                    pass