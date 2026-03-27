-- NPC: Ambra
-- Role: shopkeeper  |  Room: 10395
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "ambra"
NPC.name           = "Ambra"
NPC.article        = ""
NPC.title          = "the musician"
NPC.description    = "A vivacious elven woman surrounded by musical instruments, always humming something under her breath."
NPC.home_room_id   = 10395

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
NPC.shop_id        = 15

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "plays a brief welcoming flourish on a lute near the door."
NPC.dialogues = {
    music = "Music feeds the soul.  An adventurer who plays lives longer - trust me.",
    bards = "Bards use instruments as weapons as much as instruments.  The right song at the right moment can turn a battle.",
    instruments = "I carry lutes, flutes, harps, and several specialty instruments.  LIST to see stock.",
    buy = "LIST to see my inventory, BUY what speaks to you.",
    sell = "I'll buy quality instruments in good condition.  SELL them.",
    default = "Ambra looks up with a bright smile.  'Musical?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Ambra tunes a lute by ear with quick, confident adjustments.",
    "Ambra demonstrates a complex chord progression quietly to herself.",
    "Ambra polishes the body of a beautiful instrument with a soft cloth.",
    "Ambra hums a melody while updating her inventory.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 30

return NPC
