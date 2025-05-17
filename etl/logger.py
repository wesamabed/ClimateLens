# etl/logger.py
import logging

def get_logger(name: str = __name__, level: str = "INFO") -> logging.Logger:
    """
    Adapter Pattern:
    Centralizes logger configuration:
      • Single place to tweak format/handlers.
      • Consistent structured logs across modules.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s %(levelname)s ▶ %(message)s"
        handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
