"""Structured logging configuration.

Provides JSON-formatted structured logging with configurable levels.
Each module domain (api, service, simulation) gets its own named logger.
"""

import logging
import sys
from typing import Final

from app.core.config import get_settings

_LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
)
_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

_configured: bool = False


def setup_logging() -> None:
    """Configure the root logger and set levels from application settings.

    Safe to call multiple times — only configures once.
    """
    global _configured
    if _configured:
        return

    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any pre-existing handlers to avoid duplicate output
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quieten noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.

    Args:
        name: Logger name, typically the module domain
              (e.g. 'api.nodes', 'service.node', 'simulation.cpu').

    Returns:
        A configured logging.Logger instance.
    """
    return logging.getLogger(f"simulator.{name}")
