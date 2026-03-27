-- NPC: Elantaran
-- Role: shopkeeper  |  Room: 10364
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "elantaran"
NPC.name           = "Elantaran"
NPC.article        = ""
NPC.title          = "the alchemist"
NPC.description    = "An older elven man with ink-stained fingers and the slightly distracted air of someone whose thoughts are usually elsewhere entirely."
NPC.home_room_id   = 10364

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
NPC.shop_id        = 8

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "blinks twice as if returning from very far away.  'A customer!'"
NPC.dialogues = {
    magic = "I stock the materials practitioners of all magical disciplines require.",
    alchemy = "The art of alchemy requires patience and precision.  Both of which are in short supply these days.",
    scrolls = "I carry a modest selection of scrolls.  Nothing dangerous.  Probably.",
    potions = "My potions are properly mixed and clearly labeled.  I can't say the same for my competitors.",
    wizard = "The Wizard Guild is just around the corner if you need instruction.  I just sell the supplies.",
    buy = "LIST to see my inventory.  BUY what you require.",
    sell = "I'll purchase magical components.  SELL what you've gathered.",
    default = "Elantaran looks up from a tome.  'Hmm?  Oh.  Yes.  Can I help?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Elantaran peers at a small vial of luminescent fluid with intense concentration.",
    "Elantaran mutters under his breath while scribbling formulae in a worn notebook.",
    "Elantaran carefully decants a shimmering liquid from one flask to another.",
    "Elantaran holds two crystals side by side, comparing them with a squint.",
    "Elantaran pushes his spectacles up his nose and returns to his notes.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 30

return NPC
