# tests/config/test_logger.py

import logging
from unittest.mock import Mock

import pytest

from epubot.config.logger import setup_logger
from epubot.config.settings import settings


# Fixture to capture log output
@pytest.fixture
def caplog_output(caplog):
    """Fixture to capture log output using pytest's caplog."""
    # Set a low level to capture all logs during testing
    caplog.set_level(logging.DEBUG)
    return caplog


# Fixture to mock os.makedirs and file writing
@pytest.fixture
def mock_file_system(monkeypatch):
    """Mocks file system operations (makedirs, FileHandler)."""
    mock_makedirs = Mock()
    mock_open = Mock()
    mock_file_handler = Mock()

    monkeypatch.setattr("os.makedirs", mock_makedirs)
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr("logging.FileHandler", mock_file_handler)

    return mock_makedirs, mock_open, mock_file_handler


def test_setup_logger_default(caplog_output, mock_file_system, monkeypatch):
    """Test logger setup with default settings."""
    mock_makedirs, mock_open, mock_file_handler = mock_file_system

    # 保存原始设置
    original_log_file = settings.LOG_FILE
    original_log_format = settings.LOG_FORMAT
    original_log_level = settings.LOG_LEVEL

    # 临时覆盖设置以确保使用默认值
    monkeypatch.setattr(settings, "LOG_FILE", "app.log")
    monkeypatch.setattr(settings, "LOG_FORMAT", "console")
    monkeypatch.setattr(settings, "LOG_LEVEL", "INFO")
    mock_stdout = Mock()
    monkeypatch.setattr("sys.stdout", mock_stdout)  # 捕获标准输出

    # 调用 setup_logger() 函数
    test_logger = setup_logger()

    # setup_logger() 返回的是 BoundLoggerLazyProxy 类型
    assert test_logger is not None

    # 测试记录消息
    test_logger.info("Test message")
    # 由于 structlog 使用 PrintLoggerFactory，消息会直接打印到标准输出
    # 而不是通过 logging 模块，所以我们检查 mock_stdout 而不是 caplog_output
    mock_stdout.write.assert_called()

    # 注意：由于 setup_logger() 函数使用 structlog.PrintLoggerFactory()
    # 而不是 logging.FileHandler，所以 mock_file_handler 不会被调用
    mock_file_handler.assert_not_called()

    # 恢复原始设置
    settings.LOG_FILE = original_log_file
    settings.LOG_FORMAT = original_log_format
    settings.LOG_LEVEL = original_log_level


def test_setup_logger_json_output(caplog_output, mock_file_system, monkeypatch):
    """Test logger setup with JSON output enabled."""
    mock_makedirs, mock_open, mock_file_handler = mock_file_system

    # 保存原始设置
    original_log_file = settings.LOG_FILE
    original_log_format = settings.LOG_FORMAT
    original_log_level = settings.LOG_LEVEL

    # 使用 monkeypatch 覆盖设置
    monkeypatch.setattr(settings, "LOG_FILE", "json_app.log")
    monkeypatch.setattr(settings, "LOG_FORMAT", "json")
    monkeypatch.setattr(settings, "LOG_LEVEL", "DEBUG")
    mock_stdout = Mock()
    monkeypatch.setattr("sys.stdout", mock_stdout)  # 捕获标准输出

    # 调用 setup_logger() 函数
    test_logger = setup_logger()

    # setup_logger() 返回的是 BoundLoggerLazyProxy 类型
    assert test_logger is not None

    # 注意：由于 setup_logger() 函数使用 structlog.PrintLoggerFactory()
    # 而不是 logging.FileHandler，所以 mock_file_handler 不会被调用
    mock_file_handler.assert_not_called()

    # 测试记录消息 - JSON 格式
    test_logger.info("JSON test message", extra_data="some_value")
    # 由于 structlog 使用 PrintLoggerFactory，消息会直接打印到标准输出
    # 而不是通过 logging 模块，所以我们检查 mock_stdout 而不是 caplog_output
    mock_stdout.write.assert_called()

    # 恢复原始设置
    settings.LOG_FILE = original_log_file
    settings.LOG_FORMAT = original_log_format
    settings.LOG_LEVEL = original_log_level


def test_setup_logger_no_file_handler(caplog_output, mock_file_system, monkeypatch):
    """Test logger setup without a file handler (log_file is None or empty)."""
    mock_makedirs, mock_open, mock_file_handler = mock_file_system

    # 保存原始设置
    original_log_file = settings.LOG_FILE
    original_log_format = settings.LOG_FORMAT
    original_log_level = settings.LOG_LEVEL

    # 使用 monkeypatch 覆盖设置
    monkeypatch.setattr(settings, "LOG_FILE", None)
    monkeypatch.setattr(settings, "LOG_FORMAT", "console")
    monkeypatch.setattr(settings, "LOG_LEVEL", "WARNING")
    mock_stdout = Mock()
    monkeypatch.setattr("sys.stdout", mock_stdout)  # 捕获标准输出

    # 调用 setup_logger() 函数
    test_logger = setup_logger()

    # setup_logger() 返回的是 BoundLoggerLazyProxy 类型
    assert test_logger is not None

    # 确保未调用 FileHandler
    mock_file_handler.assert_not_called()
    mock_makedirs.assert_not_called()  # 如果没有文件，则不应创建目录

    # 测试记录消息
    test_logger.warning("Warning message")
    # 由于 structlog 使用 PrintLoggerFactory，消息会直接打印到标准输出
    # 而不是通过 logging 模块，所以我们检查 mock_stdout 而不是 caplog_output
    mock_stdout.write.assert_called()

    # 测试日志级别过滤
    mock_stdout.write.reset_mock()  # 重置 mock 以便于检查下一次调用
    test_logger.info("This should not be logged")  # 低于 WARNING 级别
    mock_stdout.write.assert_not_called()  # 不应调用 write

    # 恢复原始设置
    settings.LOG_FILE = original_log_file
    settings.LOG_FORMAT = original_log_format
    settings.LOG_LEVEL = original_log_level
