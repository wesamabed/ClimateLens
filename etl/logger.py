import logging

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Returns a logger that:
      • Streams to stdout
      • Uses a consistent timestamped format
      • Honors the requested level
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s %(levelname)s ▶ %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger
