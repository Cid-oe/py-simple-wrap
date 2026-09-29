"""Tests for easy_logging module."""

import logging
import pytest

from py_simple_package.src.py_simple.easy_logging import (
    setup_file_logger,
)


@pytest.fixture(autouse=True)
def cleanup_logging_handlers():
    """Ensure handlers added during tests are closed and removed."""
    yield
    manager = logging.Logger.manager
    loggers = [logging.root] + [
        logging.getLogger(name) for name in manager.loggerDict
    ]
    for logger in loggers:
        for handler in list(logger.handlers):
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger.removeHandler(handler)


def test_setup_file_logger_creates_file_and_logs(tmp_path):
    log_file = tmp_path / "app.log"
    logger = setup_file_logger(str(log_file))

    logger.info("Application started successfully")

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "INFO - Application started successfully" in content


def test_setup_file_logger_respects_level_int(tmp_path):
    log_file = tmp_path / "app.log"
    logger = setup_file_logger(str(log_file), level=logging.WARNING)

    logger.info("This info message should not appear")
    logger.warning("This warning message should appear")

    content = log_file.read_text(encoding="utf-8")
    assert "This info message should not appear" not in content
    assert "WARNING - This warning message should appear" in content


def test_setup_file_logger_respects_level_str(tmp_path):
    log_file = tmp_path / "debug.log"
    logger = setup_file_logger(str(log_file), level="debug")

    logger.debug("Debug message logged via string level")

    content = log_file.read_text(encoding="utf-8")
    assert "DEBUG - Debug message logged via string level" in content


def test_setup_file_logger_custom_format(tmp_path):
    log_file = tmp_path / "custom.log"
    logger = setup_file_logger(
        str(log_file),
        format_string="[%(levelname)s] %(message)s",
    )

    logger.info("Custom formatted log line")

    content = log_file.read_text(encoding="utf-8")
    assert content.strip() == "[INFO] Custom formatted log line"


def test_setup_file_logger_creates_parent_directories(tmp_path):
    log_file = tmp_path / "nested" / "sub" / "app.log"
    logger = setup_file_logger(str(log_file))

    logger.info("Nested directory message")

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "INFO - Nested directory message" in content


def test_setup_file_logger_custom_name(tmp_path):
    log_file = tmp_path / "named.log"
    logger = setup_file_logger(str(log_file), name="my_custom_service")

    assert logger.name == "my_custom_service"
    logger.info("Named service message")

    content = log_file.read_text(encoding="utf-8")
    assert "INFO - Named service message" in content


def test_setup_file_logger_does_not_duplicate_handlers(tmp_path):
    log_file = tmp_path / "single_handler.log"
    logger1 = setup_file_logger(str(log_file))
    logger2 = setup_file_logger(str(log_file))

    assert logger1 is logger2

    file_handlers = [
        h for h in logger1.handlers if isinstance(h, logging.FileHandler)
    ]
    assert len(file_handlers) == 1

    logger1.info("Single line message")
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


def test_setup_file_logger_updates_level_on_existing_handler(tmp_path):
    log_file = tmp_path / "level_update.log"
    logger = setup_file_logger(str(log_file), level=logging.WARNING)

    logger.info("Ignored before update")

    # Reconfigure with DEBUG
    setup_file_logger(str(log_file), level=logging.DEBUG)
    logger.info("Captured after update")

    content = log_file.read_text(encoding="utf-8")
    assert "Ignored before update" not in content
    assert "INFO - Captured after update" in content


def test_setup_file_logger_imported_from_py_simple():
    from py_simple.easy_logging import (
        setup_file_logger as easy_logging_setup,
    )
    from py_simple import setup_file_logger as top_level_setup

    assert callable(easy_logging_setup)
    assert callable(top_level_setup)
    assert easy_logging_setup is top_level_setup
