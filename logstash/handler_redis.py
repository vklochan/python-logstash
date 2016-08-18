import redis
import logging
import formatter


class RedisHandler(logging.Handler):

    def __init__(self, channel, redis_client=None, host='localhost', port=6379, password=None, db=0,
                 level=logging.NOTSET, message_type='logstash', tags=None, fqdn=False, version=0):
        """
        Create a new logger for the given channel and redis_client.
        """
        super(RedisHandler, self).__init__(level)
        self.channel = channel
        self.redis_client = redis_client or redis.Redis(host=host, port=port, password=password, db=db)

        if version == 1:
            self.formatter = formatter.LogstashFormatterVersion1(message_type, tags, fqdn)
        else:
            self.formatter = formatter.LogstashFormatterVersion0(message_type, tags, fqdn)

    def emit(self, record):
        """
        Publish record to redis logging channel
        """
        try:
            self.redis_client.publish(self.channel, self.format(record))
        except redis.RedisError:
            pass