#!/usr/bin/env python3
"""
GemStone IV world authority entry point.
"""

from __future__ import annotations

import logging
import os
import signal
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("GEMSTONE_ROOT", PROJECT_ROOT)

from server.core.config import Config
from server.core.game_server import GameServer


def setup_logging(config):
    log_level = getattr(logging, config.get("logging.level", "INFO"))
    log_dir = config.get("logging.log_dir", "./logs/server")
    os.makedirs(log_dir, exist_ok=True)
    handlers = []
    if config.get("logging.console", True):
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)-20s | %(message)s",
            datefmt="%H:%M:%S"
        ))
        handlers.append(console)
    if config.get("logging.file", True):
        file_handler = logging.FileHandler(
            os.path.join(log_dir, "server.log"),
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)-20s | %(message)s"
        ))
        handlers.append(file_handler)
    logging.basicConfig(level=log_level, handlers=handlers)


def main():
    config_path = os.path.join(PROJECT_ROOT, "config", "server", "server.yml")
    config = Config(config_path)
    db_config_path = os.path.join(PROJECT_ROOT, "config", "database", "database.yml")
    config.load(db_config_path)
    setup_logging(config)
    log = logging.getLogger("world_main")
    log.info("Configuration loaded from %s", config_path)

    server = GameServer(config)

    def shutdown(signum, frame):
        log.info("Shutdown signal received (signal %d)", signum)
        server.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        server.start()
    except Exception as exc:
        log.critical("World authority failed to start: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
