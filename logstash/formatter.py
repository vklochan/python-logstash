import traceback
import logging
import socket
import sys
from datetime import datetime

try:
    import json
except ImportError:
    import simplejson as json


# a mapping of attribute names on log record to output keys
# contains only those that need a mapping, fallback is record attribute name
field_map = {
    'name': 'logger',
}


def format_field(record_key, value):
    """
    Apply special formatting to certain record fields.

    :param record_key: record attribute name
    :param value: attribute value to format
    :return: the formatted value or original value
    """
    if record_key == 'exc_info':
        return ''.join(traceback.format_exception(*value)) if value else ''

    return value


class LogstashFormatterBase(logging.Formatter):
    def __init__(self, message_type='Logstash', tags=None, fqdn=False,
            default_fields=None, exc_fields=None):
        self.message_type = message_type
        self.tags = tags if tags is not None else []

        self.default_fields = default_fields \
            if default_fields is not None \
            else (
                'levelname',
                'name',
            )
        self.exc_fields = exc_fields \
            if exc_fields is not None \
            else (
                'exc_info',
                'funcName',
                'lineno',
                'process',
                'processName',
                'threadName',
            )

        if fqdn:
            self.host = socket.getfqdn()
        else:
            self.host = socket.gethostname()

    @staticmethod
    def get_extra_fields(record):
        # The list contains all the attributes listed in
        # http://docs.python.org/library/logging.html#logrecord-attributes
        skip_list = (
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'extra')

        if sys.version_info < (3, 0):
            easy_types = (basestring, bool, dict, float, int, list, type(None))
        else:
            easy_types = (str, bool, dict, float, int, list, type(None))

        fields = {}

        for key, value in record.__dict__.items():
            if key not in skip_list:
                if isinstance(value, easy_types):
                    fields[key] = value
                else:
                    fields[key] = repr(value)

        return fields

    @staticmethod
    def get_fields(record, field_names):
        """
        Get a dict with key/value pairs for all fields in `field_names` from 
        the `record`. Keys are translated according to the `field_map` and
        special values formatted using `format_field()`.

        :param record: log record
        :param field_names: list of record attribute names
        :return: dict, ready for output
        """
        return dict([
            (
                field_map.get(record_key, record_key),
                format_field(record_key, getattr(record, record_key, None))
            )
            for record_key
            in field_names
        ])

    @classmethod
    def format_source(cls, message_type, host, path):
        return "%s://%s/%s" % (message_type, host, path)

    @classmethod
    def format_timestamp(cls, time):
        tstamp = datetime.utcfromtimestamp(time)
        return tstamp.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % \
            (tstamp.microsecond / 1000) + "Z"

    @classmethod
    def serialize(cls, message):
        if sys.version_info < (3, 0):
            return json.dumps(message)
        else:
            return bytes(json.dumps(message), 'utf-8')


class LogstashFormatterVersion0(LogstashFormatterBase):
    version = 0

    def format(self, record):
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@message': record.getMessage(),
            '@source': self.format_source(self.message_type, self.host,
                record.pathname),
            '@source_host': self.host,
            '@source_path': record.pathname,
            '@tags': self.tags,
            '@type': self.message_type,
        }

        # Add default extra fields
        message['@fields'].update(self.get_fields(record, self.default_fields))

        # Add extra fields
        message['@fields'].update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message['@fields'].update(self.get_fields(record, self.exc_fields))

        return self.serialize(message)


class LogstashFormatterVersion1(LogstashFormatterBase):
    def format(self, record):
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': 1,
            'message': record.getMessage(),
            'host': self.host,
            'path': record.pathname,
            'tags': self.tags,
            'type': self.message_type,
        }

        # Add default extra fields
        message.update(self.get_fields(record, self.default_fields))

        # Add extra fields
        message.update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_fields(record, self.exc_fields))

        return self.serialize(message)
