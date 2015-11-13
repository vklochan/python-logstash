import logging.config

host = 'localhost'

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'logstash_v1_with_thread_name': {
            '()': 'logstash.LogstashFormatterVersion1',
            'extra_fields': ['threadName', 'process'],
        },
    },
    'handlers': {
        'logstash': {
            'class': 'logstash.LogstashHandler',
            'formatter': 'logstash_v1_with_thread_name',
            'host': host,
            'port': 5959,
        }
    },
    'root': {
        'handlers': ['logstash']
    },
})

test_logger = logging.getLogger('python-logstash-logger')

test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
test_logger.warning('python-logstash: test logstash warning message.')
