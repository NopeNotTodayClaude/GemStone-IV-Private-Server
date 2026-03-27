-- NPC: High Priest Vaerindas
-- Role: townsfolk  |  Room: 10369
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "arkarti_priest"
NPC.name           = "High Priest Vaerindas"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A solemn elven priest in elaborate ceremonial robes bearing the symbols of multiple Arkati deities."
NPC.home_room_id   = 10369

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "bows his head in solemn welcome."
NPC.dialogues = {
    arkati = "The Arkati shaped this world.  We honor all of them here.",
    prayer = "Any may pray here regardless of faith.  All Arkati are welcome in this hall.",
    shrine = "Each alcove is dedicated to a different Arkati.  Find the one that speaks to you.",
    lorminstra = "The Lady of the Dead watches over those who die bravely.  She is not to be feared.",
    default = "High Priest Vaerindas speaks quietly.  'Welcome, seeker.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "High Priest Vaerindas lights a candle before a shrine with reverent hands.",
    "High Priest Vaerindas leads a quiet prayer, his voice barely above a whisper.",
    "High Priest Vaerindas adjusts the offerings arranged before each altar.",
    "High Priest Vaerindas pauses before each shrine in turn, offering a few silent words.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
