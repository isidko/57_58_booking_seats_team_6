import logging
import sys

from loguru import logger

from app.core.config import settings
from app.core.log_level import LogLevel

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


class InterceptHandler(logging.Handler):
    """Handler that intercepts standard logging records.

    For details see this:
    https://medium.com/@muh.bazm/how-i-unified-logging-in-fastapi-with-uvicorn-and-loguru-6813058c48fc
    Forwards them to loguru logger.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to loguru logger."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_back and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).bind(
            user_id=None, username="SYSTEM",
        ).log(level, record.getMessage())


loggers = (
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "fastapi",
    "asyncio",
    "starlette",
)

for logger_name in loggers:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = []
    logging_logger.propagate = True

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)


def configure_logging() -> None:
    """Configure logger. File and console."""
    logger.remove()
    enable_exception_catching = settings.environment in ("LOCAL", "STAGING")

    if settings.environment == "PRODUCTION":
        logger.add(
            "app/logfile.log",  # todo deal wth this when dockerizing the app!
            rotation="500 MB",
            compression="zip",
            format=(
                "{time} | {level} | user_id={extra[user_id]} : "
                "username={extra[username]} | {message}"
            ),
            backtrace=False,
            diagnose=False,
            level=settings.loglevel,
        )
    logger.add(
        sys.stderr,
        format=(
            "<green>{time}</green> | "
            "<level>{level}</level> | "
            "<cyan>user_id={extra[user_id]}</cyan> : "
            "<cyan>username={extra[username]}</cyan> | "
            "{message}"
        ),
        colorize=True,
        backtrace=enable_exception_catching,
        diagnose=enable_exception_catching,
        level=settings.loglevel,
    )


def log_message(
        message: str,
        level: LogLevel = LogLevel.INFO,
        user_id: int | None = None,
        username: str = "SYSTEM",
) -> None:
    """Log message with some kwargs."""
    logger.bind(user_id=user_id, username=username).log(level, message)
