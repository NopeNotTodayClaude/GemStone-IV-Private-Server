-- NPC: Vonder
-- Role: shopkeeper  |  Room: 10362
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "vonder"
NPC.name           = "Vonder"
NPC.article        = ""
NPC.title          = "the fletcher"
NPC.description    = "A rangy elven man with sharp eyes and the perpetually ink-stained fingers of someone who spends as much time designing shafts as selling them."
NPC.home_room_id   = 10362

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
NPC.shop_id        = 13

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks up from fletching and gives a measured nod."
NPC.dialogues = {
    arrows = "I stock hunting, war, and specialty arrows.  LIST to see current inventory.",
    bows = "I carry several bow types.  A good bow is an investment - don't skimp.",
    fletching = "I make all my arrows in-house.  Consistent spine weight, proper feathering.  The good stuff.",
    ranged = "Ranged combat is underrated.  A crossbow can turn the tide before the enemy reaches you.",
    training = "Get Ranged Weapons ranks.  A bow is useless in untrained hands.",
    buy = "LIST to browse, BUY to purchase.",
    sell = "I'll buy back undamaged arrows and quality bows.  SELL them.",
    default = "Vonder nods.  'Looking for something to shoot with or something to shoot?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Vonder attaches a goose-feather fletching to an arrow shaft with practiced speed.",
    "Vonder draws a bow to full draw and releases the empty string, listening to the tone.",
    "Vonder inspects the straightness of an arrow shaft with one eye closed.",
    "Vonder waxes a bowstring methodically from end to end.",
    "Vonder sorts arrows by weight into labeled bundles.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 40

return NPC
