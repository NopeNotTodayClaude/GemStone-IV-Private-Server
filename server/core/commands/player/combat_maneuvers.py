"""
combat_maneuvers.py
-------------------
Player-facing CMAN command entry points.
"""

from __future__ import annotations

from server.core.scripting.lua_bindings.combat_maneuver_api import handle_cman_command


async def cmd_cman(session, cmd: str, args: str, server):
    await handle_cman_command(session, cmd, args, server)
