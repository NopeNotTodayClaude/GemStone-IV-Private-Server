#!/usr/bin/env python3
"""
GemStone IV Private Server - Main Entry Point
"""

import sys
import os
import signal
import logging

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from server.core.config import Config
from server.core.game_server import GameServer


def setup_logging(config):
    """Configure logging based on server config."""
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
    print(r"""
   ____                ____  _                     _______     __
  / ___| ___ _ __ ___ / ___|| |_ ___  _ __   ___  |_ _\ \   / /
 | |  _ / _ \ '_ ` _ \\___ \| __/ _ \| '_ \ / _ \  | | \ \ / /
 | |_| |  __/ | | | | |___) | || (_) | | | |  __/  | |  \ V /
  \____|\___|_| |_| |_|____/ \__\___/|_| |_|\___| |___|  \_/

                    Private Server v0.1.0
    """)

    # Load configuration (server + database)
    config_path = os.path.join(PROJECT_ROOT, "config", "server", "server.yml")
    config = Config(config_path)

    db_config_path = os.path.join(PROJECT_ROOT, "config", "database", "database.yml")
    config.load(db_config_path)

    # Setup logging
    setup_logging(config)
    log = logging.getLogger("main")
    log.info("Configuration loaded from %s", config_path)

    # Create and start the game server
    server = GameServer(config)

    # Graceful shutdown handler
    def shutdown(signum, frame):
        log.info("Shutdown signal received (signal %d)", signum)
        server.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        server.start()
    except Exception as e:
        log.critical("Server failed to start: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
