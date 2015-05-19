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
        open('/tmp/UnixLogstashHandler.log', 'ab').write('Connecting\n')
        self.sock.connect(socket_name)
        open('/tmp/UnixLogstashHandler.log', 'ab').write('Connected\n')
        #self.socket_name = socket_name

        #self.output_file = open('/tmp/UnixLogstashHandler.log', 'wb')

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

        """
        backoff_time = 0.001
        sent = False

        while not sent:
            try:
                self.sock.sendall(formatted_record)
                sent = True
            except socket.error as e:
                self.output_file.write('Got socket.error number %d, Sleeping %.3f\n' % (e.errno, backoff_time))
                self.output_file.flush()
            except IOError:
                self.output_file.write('Got IOError, Sleeping %.3f\n' % backoff_time)
                self.output_file.flush()

            if not sent:
                self.sock.close()
                time.sleep(backoff_time)
                backoff_time *= (1.5 + 1 * random.random())

                try:
                    self.sock.connect(self.socket_name)
                    self.output_file.write("Connecting again to %s\n" % self.socket_name)
                    self.output_file.flush()
                except IOError as (no, strerror):
                    self.output_file.write("I/O error({0}): {1}\n".format(no, strerror))
                    self.output_file.flush()

                    self.output_file.write('self.sock.connect failed\n')
                    self.output_file.flush()
        """