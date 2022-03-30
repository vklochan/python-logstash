import ssl
from logging.handlers import SocketHandler
from logstash import formatter


# Derive from object to force a new-style class and thus allow super() to work
# on Python 2.6
class TCPLogstashHandler(SocketHandler, object):
    """Python logging handler for Logstash. Sends events over TCP.
    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 5959).
    :param message_type: The type of the message (default logstash).
    :param fqdn; Indicates whether to show fully qualified domain name or not (default False).
    :param version: version of logstash event schema (default is 0).
    :param tags: list of tags for a logger (default is None).
    :param ssl: Should SSL be enabled for the connection? Default is True.
    :param ssl_verify: Should the server's SSL certificate be verified?
    :param keyfile: The path to client side SSL key file (default is None).
    :param certfile: The path to client side SSL certificate file (default is None).
    :param ca_certs: The path to the file containing recognised CA certificates. System wide CA certs are used if omitted.
    """

    def __init__(self, host, port=5959, message_type='logstash', tags=None, fqdn=False, version=0, ssl=True, ssl_verify=True, keyfile=None, certfile=None, ca_certs=None):
        super(TCPLogstashHandler, self).__init__(host, port)

        self.ssl = ssl
        self.ssl_verify = ssl_verify
        self.keyfile = keyfile
        self.certfile = certfile
        self.ca_certs = ca_certs

        if version == 1:
            self.formatter = formatter.LogstashFormatterVersion1(message_type, tags, fqdn)
        else:
            self.formatter = formatter.LogstashFormatterVersion0(message_type, tags, fqdn)

    def makePickle(self, record):
        return self.formatter.format(record) + b'\n'


    def makeSocket(self, timeout=1):
        s = super(TCPLogstashHandler, self).makeSocket(timeout)

        if not self.ssl:
            return s

        context = ssl.create_default_context(cafile=self.ca_certs)
        context.verify_mode = ssl.CERT_REQUIRED
        if not self.ssl_verify:
            if self.ca_certs:
                context.verify_mode = ssl.CERT_OPTIONAL
            else:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

        # Client side certificate auth.
        if self.certfile and self.keyfile:
            context.load_cert_chain(self.certfile, keyfile=self.keyfile)

        return context.wrap_socket(s, server_hostname=self.host)
