#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logstash


class CustomFormatter(logstash.LogstashFormatterBase):
    def format(self, record):
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': '1',
            'message': record.getMessage(),
            'type': 'custom',

            'custom_key': 'This is a custom item',
            'thread_name': record.threadName
        }

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)

host = 'localhost'

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.TCPLogstashHandler(host, 5959, custom_formatter=CustomFormatter))

test_logger.error('python-logstash: test logstash error message with custom formatter.')
test_logger.info('python-logstash: test logstash info message with custom formatter.')
test_logger.warning('python-logstash: test logstash warning message with custom formatter.')
