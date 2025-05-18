import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import structlog
from structlog.types import Processor

# Import settings after the package structure is defined
from epubot.config.settings import settings


def setup_logger():
    """配置结构化日志并返回一个logger实例"""

    # 创建日志目录（如果不存在）
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建根日志处理器
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # 清除任何现有的处理器
    if root_logger.handlers:
        root_logger.handlers.clear()

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(console_handler)

    # 添加文件处理器（使用RotatingFileHandler以防日志文件过大）
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(file_handler)

    # 定义共享处理器
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    if settings.LOG_FORMAT == "json":
        # JSON格式的日志
        shared_processors.extend(
            [
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),  # 移除 serializer=str
            ]
        )
    else:
        # 控制台格式的日志
        shared_processors.extend(
            [
                structlog.dev.ConsoleRenderer(
                    colors=True, exception_formatter=structlog.dev.plain_traceback
                )
            ]
        )

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL)
        ),
        cache_logger_on_first_use=True,
    )

    # Return a logger instance
    return structlog.get_logger()


# Initialize logger from settings
logger = setup_logger()
