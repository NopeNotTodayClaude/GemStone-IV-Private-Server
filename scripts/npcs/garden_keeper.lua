-- NPC: Groundskeeper Mirthiel
-- Role: townsfolk  |  Room: 10373
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "garden_keeper"
NPC.name           = "Groundskeeper Mirthiel"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A weathered elven gardener with dirt under his fingernails and genuine love for his ancient charges."
NPC.home_room_id   = 10373

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
NPC.greeting       = "looks up from pruning and gives a warm, earthy smile."
NPC.dialogues = {
    garden = "These trees are over three thousand years old.  Every one has a name.",
    plants = "I know every plant in this garden.  Each one is a piece of living history.",
    history = "The founders of Ta'Vaalor planted these trees.  They're all that remains of that age.",
    names = "That one there is called Vaelorn.  The one beside it is Taeris.  The tall one in back is simply Old One.  She was here before us.",
    default = "Mirthiel pats a tree trunk affectionately.  'She's a beauty, isn't she?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Groundskeeper Mirthiel prunes a branch with careful, deliberate snips.",
    "Groundskeeper Mirthiel kneels to examine the roots of an ancient oak.",
    "Groundskeeper Mirthiel waters the garden beds with a battered copper can.",
    "Groundskeeper Mirthiel touches the bark of the oldest tree gently, as if greeting an old friend.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
