"""
Zone - Represents a game zone/area loaded from Lua.
"""

import os
import logging
from typing import Dict

log = logging.getLogger(__name__)


class Zone:
    """A game zone containing rooms, NPCs, and creatures."""

    def __init__(self):
        self.id = 0
        self.slug = ""           # directory name / key
        self.name = "Unknown"
        self.region = "Unknown"
        self.level_min = 1
        self.level_max = 100
        self.climate = "temperate"
        self.indoor = False
        self.rooms: Dict[int, 'Room'] = {}

    @classmethod
    def from_db_row(cls, row: dict) -> 'Zone':
        """Construct a Zone from a database row (zones table)."""
        zone = cls()
        zone.id        = int(row["id"])
        zone.slug      = row.get("slug", "")
        zone.name      = row.get("name", zone.slug.replace("_", " ").title())
        zone.region    = row.get("region", "Unknown")
        zone.level_min = int(row.get("level_min", 1))
        zone.level_max = int(row.get("level_max", 100))
        zone.climate   = row.get("climate", "temperate")
        zone.indoor    = False
        return zone

    @classmethod
    def load_from_lua(cls, slug, zone_path):
        """Load zone metadata from a zone.lua file."""
        zone = cls()
        zone.slug = slug

        zone_file = os.path.join(zone_path, "zone.lua")

        # Parse the Lua file for zone properties
        # For now, use a simple key-value parser
        # Later we'll switch to full Lua execution via lupa
        zone_data = cls._parse_lua_table(zone_file)

        zone.id = zone_data.get("id", 0)
        zone.name = zone_data.get("name", slug.replace("_", " ").title())
        zone.region = zone_data.get("region", "Unknown")
        zone.level_min = zone_data.get("level_min", 1)
        zone.level_max = zone_data.get("level_max", 100)
        zone.climate = zone_data.get("climate", "temperate")
        zone.indoor = zone_data.get("indoor", False)

        return zone

    @staticmethod
    def _parse_lua_table(filepath):
        """
        Simple Lua table parser for zone/room config.
        Extracts 'TableName.key = value' patterns.
        This is a bootstrap parser - will be replaced by lupa later.
        """
        data = {}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("--") or line.startswith("function"):
                        continue
                    # Match patterns like: Zone.name = "Something"
                    if "=" in line and not line.startswith("local") and not line.startswith("return"):
                        parts = line.split("=", 1)
                        key_part = parts[0].strip()
                        val_part = parts[1].strip().rstrip(",")

                        # Extract key after the dot
                        if "." in key_part:
                            key = key_part.split(".", 1)[1].strip()
                        else:
                            continue

                        # Parse value
                        if val_part.startswith('"') and val_part.endswith('"'):
                            data[key] = val_part.strip('"')
                        elif val_part.startswith("'") and val_part.endswith("'"):
                            data[key] = val_part.strip("'")
                        elif val_part.lower() == "true":
                            data[key] = True
                        elif val_part.lower() == "false":
                            data[key] = False
                        elif val_part.isdigit():
                            data[key] = int(val_part)
                        else:
                            try:
                                data[key] = float(val_part)
                            except ValueError:
                                data[key] = val_part

        except Exception as e:
            log.error("Error parsing Lua file %s: %s", filepath, e)

        return data

    def __repr__(self):
        return f"Zone({self.slug}, rooms={len(self.rooms)})"
