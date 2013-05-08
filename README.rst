python-logstash
===============

Python logging handler for Logstash.

Installation
============

Using pip::

  pip install python-logstash

Using example
=============

``LogstashHandler`` is a custom logging handler which sends Logstash messages using UDP.

For example::

  import logging
  import logstash

  test_logger = logging.getLogger('test_logger')
  test_logger.setLevel(logging.INFO)
  test_logger.addHandler(logstash.LogstashHandler('localhost', 5959))

  test_logger.info('Test logstash message.')

Using with Django
=================

Modify your ``settings.py`` to integrate ``python-logstash`` with Django's logging::

  LOGGING = {
    ...
    'handlers': {
        'logstash': {
            'level': 'DEBUG',
            'class': 'logstash.LogstashHandler',
            'host': 'localhost',
            'port': 5959,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['logstash'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    ...
  }
