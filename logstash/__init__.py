try:
    from handler import LogstashHandler
except ImportError:
    from .handler import LogstashHandler