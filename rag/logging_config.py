from __future__ import annotations

import logging

from configs.settings import LOG_DIR


def configure_logging() -> None:
    """Configure project-wide logging once."""
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "rag.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=False,
    )
