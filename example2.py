import logging
import logstash

# AMQP parameters
host = 'localhost'
username = 'guest'
password= 'guest'
exchange = 'logstash.py'

# get a logger and set logging level
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)

# add the handler
test_logger.addHandler(logstash.AMQPLogstashHandler(version=1,
                                                    host=host,
                                                    durable=True,
                                                    username=username,
                                                    password=password,
                                                    exchange=exchange))

# log
test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
test_logger.warning('python-logstash: test logstash warning message.')

try:
    1/0
except:
    test_logger.exception('python-logstash: test logstash exception with stack trace')
