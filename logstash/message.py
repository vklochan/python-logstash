from abc import ABCMeta, abstractmethod
from datetime import datetime
import json

class LogstashMessageBase(object):
    """
    Base class for all message formats.
    """
    __metaclass__ = ABCMeta

    message_dict = {}

    @abstractmethod
    def setExtraField(self, name, value):
        pass

    def get_dict(self):
        return self.message_dict

    def get_json(self):
        return json.dumps(self.get_dict())

    @classmethod
    def format_source(cls, message_type, host, path):
        return "%s://%s/%s" % (message_type, host, path)

    @classmethod
    def format_timestamp(cls, time):
        return datetime.utcfromtimestamp(time).isoformat() + 'Z'


class LogstashMessageVersion0(LogstashMessageBase):
    """
    Implementation of logstash message format - version 0.
    """
    def __init__(self, message, host, path, tags, timestamp, message_type, levelname, logger):
        self.message_dict = {
            '@timestamp': self.format_timestamp(timestamp),
            '@fields': {
                'levelname': levelname,
                'logger': logger,
            },
            '@message': message,
            '@source': self.format_source(message_type, host, path),
            '@source_host': host,
            '@source_path': path,
            '@tags': tags,
            '@type': message_type,
        }

    def setExtraField(self, name, value):
        self.message_dict['@fields'][name] = value


class LogstashMessage(LogstashMessageBase):
    """
    Implementation of logstash message format - version 1.
    """
    def __init__(self, message, host, path, tags, timestamp, message_type, levelname, logger):
        self.message_dict = {
            '@timestamp': self.format_timestamp(timestamp),
            '@version': 1,
            'levelname': levelname,
            'logger': logger,
            'message': message,
            'host': host,
            'path': path,
            'tags': tags,
            'type': message_type,
        }

    def setExtraField(self, name, value):
        self.message_dict[name] = value
