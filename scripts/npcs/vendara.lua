-- NPC: Vendara
-- Role: shopkeeper  |  Room: 17292
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "vendara"
NPC.name           = "Vendara"
NPC.article        = ""
NPC.title          = "the tailor"
NPC.description    = "A neat elven man with an impeccable sense of style and a tape measure perpetually draped around his neck."
NPC.home_room_id   = 17292

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = true
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Shop ─────────────────────────────────────────────────────────────────────
NPC.shop_id        = 10

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks you up and down and nods thoughtfully."
NPC.dialogues = {
    clothes = "I stock the finest readymade garments in the city.  Custom work by appointment.",
    fashion = "Proper attire matters.  Even adventurers should look presentable between hunts.",
    custom = "For custom fitting speak to me privately.  Allow three days for quality work.",
    buy = "LIST to see my selection.  BUY what suits your taste.",
    sell = "I'll buy quality garments if they're in good condition.  SELL to me.",
    default = "Vendara looks you up and down with professional assessment.  'I can work with this.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Vendara smooths a display doublet on its mannequin with critical precision.",
    "Vendara measures a bolt of crimson fabric with practiced hands.",
    "Vendara marks a chalk line on a partially finished tunic.",
    "Vendara pins a hem into place, biting his lip in concentration.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
