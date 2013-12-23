import logging
import logstash
import sys

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.LogstashHandler('localhost', 5959, version=1))

test_logger.error('python-logstash: test logstash error.')

# test adapter
adapter = logging.LoggerAdapter(test_logger, None)
adapter.extra = {
                    'test_string': 'python version: ' + repr(sys.version_info),
                    'test_boolean': True,
                    'test_dict': {'a': 1, 'b': 'c'},
                    'test_float': 1.23,
                    'test_integer': 123,
                    'test_list': [1, 2, '3'],
                }
adapter.info('python-logstash: test logging adapter.')
