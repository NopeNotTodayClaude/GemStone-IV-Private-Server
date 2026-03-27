-- NPC: Maraene
-- Role: shopkeeper  |  Room: 10396
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "maraene"
NPC.name           = "Maraene"
NPC.article        = ""
NPC.title          = "the herbalist"
NPC.description    = "A serene elven woman with knowing eyes, surrounded by the rich scent of dried herbs.  Glass jars and ceramic pots line every surface, each labeled in flowing elven script."
NPC.home_room_id   = 10396

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
NPC.shop_id        = 5

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "smiles warmly and gestures toward shelves lined with colorful tinctures."
NPC.dialogues = {
    herbs = "I carry tinctures for every wound and ailment.  LIST to see what's available.",
    healing = "Acantha leaf for bleeding.  Wolifrew lichen for minor cuts.  Sovyn clove for the most serious injuries.",
    tinctures = "Each tincture is carefully prepared from the finest herbs grown near Ta'Vaalor.",
    empath = "I supplement what the empaths can't always get to.  We work well together.",
    stock = "Stock up before you hunt.  Running out underground is a miserable experience.",
    buy = "LIST my stock, then BUY what you need.  A wise adventurer stocks up.",
    sell = "I'll purchase quality herbs if you have any.  Just SELL them.",
    default = "Maraene smiles warmly.  'What ails you, traveler?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Maraene grinds dried herbs with a mortar and pestle, filling the air with a pleasant aroma.",
    "Maraene carefully labels a small glass vial with flowing elven script.",
    "Maraene arranges bundles of dried herbs on a wooden drying rack.",
    "Maraene examines a sprig of wolifrew, nodding at its quality.",
    "Maraene holds a tincture up to the light, checking its color and clarity.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
