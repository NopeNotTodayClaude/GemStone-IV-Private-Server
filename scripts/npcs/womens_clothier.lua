-- NPC: Raeliveth
-- Role: shopkeeper  |  Room: 17293
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "womens_clothier"
NPC.name           = "Raeliveth"
NPC.article        = ""
NPC.title          = "the clothier"
NPC.description    = "A graceful elven woman with an eye for color and a tape measure worn like jewelry.  She moves through her shop with the unhurried confidence of someone whose taste is beyond question."
NPC.home_room_id   = 17293

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
NPC.shop_id        = 16

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks up from a length of fabric with a welcoming smile."
NPC.dialogues = {
    clothes = "I carry gowns, bodices, skirts, and accessories.  LIST to browse.",
    fashion = "Presentation matters in this city.  I make sure my clients are never the worst-dressed in the room.",
    custom = "I take custom commissions.  Allow three days for quality work.",
    buy = "LIST to see my selection.  BUY what appeals to you.",
    sell = "I'll purchase quality garments in good condition.  SELL them to me.",
    default = "Raeliveth looks you over with a practiced eye.  'Something catches your fancy?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Raeliveth holds a bolt of deep crimson silk against the light, studying the drape.",
    "Raeliveth pins a hem into place on a display gown with quick, precise fingers.",
    "Raeliveth arranges a row of accessories on a velvet-covered display stand.",
    "Raeliveth adjusts the collar of a display gown with a critical tilt of her head.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
