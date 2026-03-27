-- NPC: Tmareantha
-- Role: shopkeeper  |  Room: 10327
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "tmareantha"
NPC.name           = "Tmareantha"
NPC.article        = ""
NPC.title          = "the jeweler"
NPC.description    = "An elegant elven woman whose fingers are perpetually adorned with a rotating collection of her finest work.  Every movement she makes draws attention to the gems she wears."
NPC.home_room_id   = 10327

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
NPC.shop_id        = 9

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks you over with the same expert eye she applies to gemstones."
NPC.dialogues = {
    gems = "I buy and sell gems of all kinds.  Bring me what you find in the field.",
    jewelry = "Fine jewelry is both investment and adornment.  My pieces appreciate in value.",
    appraise = "APPRAISE any gem to learn its value before you sell.",
    vaalorn = "Vaalorn-set pieces are my specialty.  The metal complements colored stones beautifully.",
    sell = "SELL me your gems.  I pay fairly for quality stones.",
    buy = "LIST my inventory.  BUY what catches your eye.",
    default = "Tmareantha looks up with cool, appraising eyes.  'Yes?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Tmareantha sets a brilliant ruby into a gold setting with delicate precision.",
    "Tmareantha examines a rough gem through a loupe, rotating it slowly.",
    "Tmareantha arranges a display of necklaces on a velvet-covered stand.",
    "Tmareantha polishes a finished brooch with a soft cloth until it gleams.",
    "Tmareantha makes a note on a small card and attaches it to a ring with a ribbon.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
