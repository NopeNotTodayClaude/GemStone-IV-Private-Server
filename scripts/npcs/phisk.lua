-- NPC: Phisk
-- Role: shopkeeper  |  Room: 12348
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "phisk"
NPC.name           = "Phisk"
NPC.article        = ""
NPC.title          = "the shopkeeper"
NPC.description    = "A wiry elf with spectacles perched on his nose and an apron full of pockets.  His shop is crammed floor to ceiling with every manner of supply an adventurer might need."
NPC.home_room_id   = 12348

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
NPC.shop_id        = 4

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "adjusts his spectacles and gestures broadly at his cluttered shelves."
NPC.dialogues = {
    supplies = "I carry a little of everything!  Torches, rope, rations - you name it.",
    prices = "My prices are fair.  This is a respectable establishment, not a bazaar.",
    hunting = "Stock up on torches before heading into the catacombs.  Dark down there.",
    new = "New to Ta'Vaalor?  Talk to Sassion near the Vermilion Gate.  She always has work for capable hands.",
    buy = "LIST to browse, BUY what you need.  Simple as that.",
    sell = "I'll take most things off your hands.  SELL away.",
    default = "Phisk adjusts his spectacles.  'Need something?  I've probably got it.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Phisk rearranges items on an already overstuffed shelf.",
    "Phisk counts coins behind the counter, muttering numbers under his breath.",
    "Phisk dusts a collection of lanterns hanging from the ceiling.",
    "Phisk scribbles in a thick ledger, occasionally licking the tip of his quill.",
    "Phisk peers over his spectacles at a new shipment, muttering about the invoice.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
