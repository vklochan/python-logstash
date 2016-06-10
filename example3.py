import logging
import logstash
import sys

host = 'localhost'

test_logger = logstash.KeyValueLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.LogstashHandler(host, 5959, version=1))
# test_logger.addHandler(logstash.TCPLogstashHandler(host, 5959, version=1))

test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
test_logger.warning('python-logstash: test logstash warning message.')

# add extra fields to logstash message via kwargs
test_logger.info('python-logstash: test extra fields',
                 test_string='python version: ' + repr(sys.version_info),
                 test_boolean=True, test_dict={'a': 1, 'b': 'c'},
                 test_float=1.23, test_integer=123, test_list=[1, 2, '3'])
