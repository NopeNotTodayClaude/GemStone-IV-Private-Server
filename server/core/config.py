"""
Configuration loader - reads YAML config with dot-notation access.
"""

import os
import yaml
import logging

log = logging.getLogger(__name__)


class Config:
    """Hierarchical configuration with dot-notation access."""

    def __init__(self, config_path=None):
        self._data = {}
        if config_path and os.path.exists(config_path):
            self.load(config_path)

    def load(self, path):
        """Load a YAML config file."""
        with open(path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
            if loaded:
                self._data.update(loaded)

    def get(self, key, default=None):
        """
        Get a value using dot notation.
        Example: config.get("server.port", 4901)
        """
        keys = key.split(".")
        val = self._data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key, value):
        """Set a value using dot notation."""
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    def __repr__(self):
        return f"Config({self._data})"
