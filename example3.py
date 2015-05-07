import logging
import logstash

# Unix Socket parameters
SOCKET_NAME = '/var/run/logstash.socket'

# get a logger and set logging level
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)

# add the handler
test_logger.addHandler(
        logstash.UnixLogstashHandler(
            SOCKET_NAME, another_field='is_set'))

# log
#test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message 2.')
#test_logger.warning('python-logstash: test logstash warning message.')

#try:
#    1/0
#except:
#    test_logger.exception('python-logstash: test logstash exception with stack trace')
