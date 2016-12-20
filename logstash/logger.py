import logging


class KeyValueLogger(logging.Logger):
    """A logger that passes kwargs on to the Logstash logger via `extra`. """

    def _log(self, level, msg, args, exc_info=None, extra=None,
             stack_info=False, **kwargs):
        extra = extra or {}
        extra.update(**kwargs)
        super()._log(level, msg, args, exc_info, extra, stack_info)
