from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(
        name: str = "yacht_etl",
        log_dir: Path | None = None,
        level: int = logging.INFO,
) -> logging.Logger:
    # Writes to a rotating log file
    # Also writes to console
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicated logs if called multiple times func: setup_logger()
    if getattr(logger, '_configured', False):
        return logger
    
    # log directory
    if log_dir is None:
        # put logs in root directory
        log_dir = Path.cwd() / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / f"{name}.log"

    fmt =  logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000, # 1 MB
        #maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding='utf-8',
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(fmt)

    logger .addHandler(file_handler)
    logger .addHandler(console_handler) 

    logger.propagate = False
    logger._configured = True # type: ignore[attr-defined]
    logger.info(f"Logger '{name}' initialized. Logs will be saved to: {log_path}")

    return logger