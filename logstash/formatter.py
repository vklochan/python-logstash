import inspect
import os
import traceback
import logging
import socket
import sys
from datetime import datetime
import subprocess

try:
    import json
except ImportError:
    import simplejson as json


class LogstashFormatterBase(logging.Formatter):
    def __init__(self, server_type=None, module=None, tags=None, fqdn=False, **kwargs):
        self.tags = tags if tags is not None else []
        self.kwargs = kwargs

        if fqdn:
            self.host = socket.getfqdn()
        else:
            self.host = socket.gethostname()

        self.server_type = server_type
        self.module = module

    def get_extra_fields(self, record):
        # The list contains all the attributes listed in
        # http://docs.python.org/library/logging.html#logrecord-attributes
        skip_list = (
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'extra')

        if sys.version_info < (3, 0):
            easy_types = (basestring, bool, dict, float, int, long, list, type(None))
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

    def get_debug_fields(self, record):
        fields = {
            'exc_info': self.format_exception(record.exc_info),
            'lineno': record.lineno,
            'process': record.process,
            'threadName': record.threadName,
        }

        # funcName was added in 2.5
        if not getattr(record, 'funcName', None):
            fields['funcName'] = record.funcName

        # processName was added in 2.6
        if not getattr(record, 'processName', None):
            fields['processName'] = record.processName

        return fields

    @classmethod
    def format_source(cls, message_type, host, path):
        return "%s://%s/%s" % (message_type, host, path)

    @classmethod
    def format_timestamp(cls, time):
        tstamp = datetime.utcfromtimestamp(time)
        return tstamp.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (tstamp.microsecond / 1000) + "Z"

    @classmethod
    def format_exception(cls, exc_info):
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''

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
            '@fields': {
                'levelname': record.levelname,
                'logger': record.name,
            },
        }

        # Add extra fields
        message['@fields'].update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message['@fields'].update(self.get_debug_fields(record))

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

            # Extra Fields
            'levelname': record.levelname,
            'logger': record.name,
        }

        # Add extra fields
        message.update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)


class MiniLogstashFormatter(LogstashFormatterBase):
    def format_base(self, record):
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created),
        }

        if self.module:
            message['module'] = self.module

        if self.server_type:
            message['server_type'] = self.server_type

        # Add configured fields
        message.update(self.kwargs)

        # Add extra fields
        message.update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        # Update fields after all others, in case the user accidentally used one of them as an extra field
        message.update({'message': record.getMessage(),
                        'host': self.host,
                        'type': '%s_%s' % (self.server_type, record.getMessage()),
                        # Extra Fields
                        'levelname': record.levelname})

        return message

    def format(self, record):
        return self.serialize(self.format_base(record))


class AWSLogstashFormatter(MiniLogstashFormatter):
    def __init__(self, cwd=None, aws_access_key_id=None, aws_secret_access_key=None, **kwargs):
        # import here so only users of the class are required to install the packages
        import boto
        import boto.ec2
        import boto.exception
        import boto.utils

        MiniLogstashFormatter.__init__(self, **kwargs)
        self.ec2_tags = {}
        try:
            metadata = boto.utils.get_instance_metadata(timeout=1)
            instance_id = metadata['instance-id']
            region = metadata['placement']['availability-zone'][:-1]  # us-east-1c -> us-east-1
            ec2_con = boto.ec2.connect_to_region(region, aws_access_key_id=aws_access_key_id,
                                                 aws_secret_access_key=aws_secret_access_key)
            inst = ec2_con.get_only_instances([instance_id])[0]
            tags = dict(env_tag=inst.tags["Environment"], server_type_tag=inst.tags["Name"])
            self.ec2_tags.update(tags)
        except (boto.exception.StandardError, IndexError, KeyError):
            raise
        self.commit_hash = subprocess.check_output(['git', 'log', '-n1', '--format=%h'], cwd=cwd).strip()
        # get the calling module's repository root directory name
        repo_path = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=cwd).strip()
        self.repo_path = os.path.split(repo_path)[1]

    def format(self, record):
        msg = self.format_base(record)
        msg.update(self.ec2_tags)
        msg['commit'] = self.commit_hash
        msg['repository'] = self.repo_path
        return self.serialize(msg)
