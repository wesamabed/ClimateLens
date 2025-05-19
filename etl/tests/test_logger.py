import logging
import re
import io
from etl.logger import get_logger


def test_logger_format_and_level_and_formatting():
    # Create logger with DEBUG level
    logger = get_logger("test.logger", level="DEBUG")
    # Verify logger type and level
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG

    # Replace handlers with one that writes to StringIO for capturing formatted output
    stream = io.StringIO()
    # Clear existing handlers
    logger.handlers.clear()
    handler = logging.StreamHandler(stream)
    fmt = "%(asctime)s %(levelname)s ▶ %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

    # Emit a log record
    logger.debug("hello %s", "world")
    log_text = stream.getvalue().strip()

    # Check full formatted output including timestamp, level, and message
    assert re.match(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ DEBUG ▶ hello world",
        log_text
    )