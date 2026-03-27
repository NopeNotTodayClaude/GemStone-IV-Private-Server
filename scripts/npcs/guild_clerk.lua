-- NPC: Thalindra
-- Role: service  |  Room: 10331
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guild_clerk"
NPC.name           = "Thalindra"
NPC.article        = ""
NPC.title          = "the guild clerk"
NPC.description    = "A businesslike elven woman who manages the Adventurers' Guild with organized efficiency and barely concealed exasperation."
NPC.home_room_id   = 10331

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
NPC.greeting       = "glances up from behind a stack of contracts.  'Another adventurer.  Lovely.'"
NPC.dialogues = {
    bounties = "I post the active bounty contracts.  Complete them for silver rewards.",
    guild = "The Adventurers' Guild connects capable individuals with those who need capable individuals.",
    register = "Guild registration is free.  You're already eligible simply by being here.",
    bounty = "Pick up a bounty, complete it, return here.  Simple as that.",
    sassion = "Sassion?  She handles the in-city errands.  Find her near the Vermilion Gate.",
    default = "Thalindra looks up.  'Bounty work?  Browse the board.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Thalindra posts a new contract on the bounty board with a decisive pin.",
    "Thalindra crosses a completed bounty off the active list.",
    "Thalindra sorts a pile of contracts by difficulty rating.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
