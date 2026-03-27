-- NPC: Maestro Velthanis
-- Role: service  |  Room: 10438
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "bard_master"
NPC.name           = "Maestro Velthanis"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "An accomplished elven bard with an elaborate lute and clothing that somehow manages to be both flamboyant and tasteful."
NPC.home_room_id   = 10438

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
NPC.greeting       = "sweeps you a theatrical bow."
NPC.dialogues = {
    bards = "The Bard Guild cultivates the finest musical and performance talents in the Elven Nations.",
    music = "Music is power.  A skilled bard can inspire armies or shatter stone with the right composition.",
    join = "We accept those with genuine talent.  Perform for me and I'll judge your potential.",
    training = "Bard training is long and demanding.  But a master bard is worth twenty soldiers.",
    songs = "Every song has a purpose.  I teach students to understand what they're actually doing, not just how.",
    default = "Maestro Velthanis strums a contemplative chord.  'Ah, a visitor.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Maestro Velthanis plays a complex melody on his lute, eyes closed.",
    "Maestro Velthanis corrects a student's fingering with a patient gesture.",
    "Maestro Velthanis composes a new piece, humming and writing simultaneously.",
    "Maestro Velthanis pauses mid-phrase, then replays it twice with tiny adjustments.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 30
NPC.guild_id        = "bard"

return NPC
