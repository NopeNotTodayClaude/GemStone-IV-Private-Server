-- NPC: Empath Laerindel
-- Role: service  |  Room: 10759
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "empath_healer"
NPC.name           = "Empath Laerindel"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A calm elven empath with gentle hands and a serene expression.  Faint silver light occasionally pulses around her fingertips."
NPC.home_room_id   = 10759

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = true
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "turns to you with a look of quiet concern.  'Are you hurt?'"
NPC.dialogues = {
    heal = "I can tend your wounds.  Empaths channel life energy to repair injury.",
    empath = "The Empath Guild trains those gifted with healing magic.  It takes years to master.",
    injuries = "Show me where it hurts.  I can handle most field injuries without difficulty.",
    join = "If you have the gift, speak to the Guild Master about joining.",
    default = "Empath Laerindel smiles gently.  'Are you injured?  I can help.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Empath Laerindel closes her eyes briefly, silver light pulsing from her hands.",
    "Empath Laerindel arranges healing supplies with practiced efficiency.",
    "Empath Laerindel tends to a patient with gentle, careful hands.",
    "Empath Laerindel takes a slow breath and centers herself before beginning work.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45
NPC.guild_id        = "empath"

return NPC
