from __future__ import annotations

import logging
import sys

from app.config import get_settings


def configure_logging() -> None:
    """Configure application logging once at startup."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
