-- NPC: Dakris
-- Role: shopkeeper  |  Room: 10379
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "dakris"
NPC.name           = "Dakris"
NPC.article        = ""
NPC.title          = "the pawnbroker"
NPC.description    = "A thin elf with a shrewd expression and a jeweler's loupe hanging from a chain around his neck.  He appraises everything with a calculating eye."
NPC.home_room_id   = 10379

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
NPC.shop_id        = 6

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "eyes you appraisingly from behind the counter."
NPC.dialogues = {
    sell = "I'll buy just about anything.  SELL me your unwanted gear for a fair price.",
    buy = "I sell what others have parted with.  LIST to see what's in stock.",
    backroom = "The back room holds the better bargains.  Use BACKROOM or LOOK ON one of the tables if you want to browse it.",
    prices = "I pay half the market value.  It's standard in the trade.  Take it or leave it.",
    appraise = "Bring me something and I'll tell you what it's worth.  Use APPRAISE.",
    gems = "Gems are always welcome.  I pay better for quality stones.",
    default = "Dakris eyes you appraisingly.  'Buying or selling?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Dakris examines a tarnished ring through his jeweler's loupe.",
    "Dakris sorts through a pile of miscellaneous goods behind the counter.",
    "Dakris polishes a second-hand blade with an oily rag.",
    "Dakris makes a note in a ledger, then taps his chin thoughtfully.",
    "Dakris holds a gemstone up to the light and squints at it critically.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
