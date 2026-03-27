-- NPC: Innkeeper Saevrin
-- Role: townsfolk  |  Room: 5826
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "inn_keeper"
NPC.name           = "Innkeeper Saevrin"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A broad-faced elf with a ready laugh and the comfortable bulk of someone who samples their own kitchen regularly."
NPC.home_room_id   = 5826

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
NPC.greeting       = "spreads his arms wide.  'Welcome to the Legendary Rest!'"
NPC.dialogues = {
    room = "Rooms are available nightly.  Clean beds, warm fire, no questions asked.",
    food = "The kitchen serves all day.  Best stew north of the Dragonspine.  I will fight anyone who says otherwise.",
    rest = "Travelers always welcome.  The Legendary Rest has stood for centuries.  So have I, more or less.",
    rumors = "You hear things in an inn.  Merchants, soldiers, travelers.  I don't repeat what I hear, but I listen.",
    default = "Innkeeper Saevrin beams.  'Room?  Board?  Both?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Innkeeper Saevrin wipes down the front desk with a cheerful hum.",
    "Innkeeper Saevrin hands a key to a weary-looking traveler.",
    "Innkeeper Saevrin calls back to the kitchen about tonight's special.",
    "Innkeeper Saevrin laughs at his own joke before anyone else gets it.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
