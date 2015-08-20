from logging import Handler
from logstash import formatter


# Derive from object to force a new-style class and thus allow super() to work
# on Python 2.6
class ZmqLogstashHandler(Handler, object):
    """Python logging handler for Logstash. Sends events over Zero-MQ socket.
    :param socket_name: The address of the server to connect to.
    """

    def __init__(self, socket_name, max_send_buff_size=10000, formatter_class=formatter.MiniLogstashFormatter, **kwargs):
        """
        Initialize a handler.
        """
        import zmq
        Handler.__init__(self)

        self.formatter = formatter_class(**kwargs)

        ctx = zmq.Context()
        self.sock = ctx.socket(zmq.PUB)
        self.sock.setsockopt(zmq.SNDHWM, max_send_buff_size)
        self.sock.connect(socket_name)

    def emit(self, record):
        """
        Emit a record.
        """
        formatted_record = self.formatter.format(record)
        self.sock.send_pyobj(formatted_record)

        return

    def __del__(self):
        try:
            self.sock.close()
        except:
            pass