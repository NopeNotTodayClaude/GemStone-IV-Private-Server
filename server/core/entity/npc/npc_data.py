"""
npc_data.py
-----------
All NPC definitions have been migrated to Lua.
Every NPC now lives in scripts/npcs/<template_id>.lua

This file intentionally contains no NPC data.
NPCManager loads all NPCs from the Lua files at startup.

Do NOT add NPC data here. Add a Lua file to scripts/npcs/ instead.
"""

# Empty — NPCManager reads from scripts/npcs/*.lua exclusively.
NPC_TEMPLATES: list = []
