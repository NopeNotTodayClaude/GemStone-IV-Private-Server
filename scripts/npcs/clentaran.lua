-- NPC: Clentaran
-- Role: shopkeeper  |  Room: 10372
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "clentaran"
NPC.name           = "Clentaran"
NPC.article        = ""
NPC.title          = "the cleric supplier"
NPC.description    = "A quiet elven man with a serenity that suggests either deep faith or complete indifference.  His shop is organized with almost liturgical precision."
NPC.home_room_id   = 10372

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
NPC.shop_id        = 12

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "bows his head in quiet greeting."
NPC.dialogues = {
    supplies = "I carry everything a cleric of any faith might require.  Holy symbols, incense, ritual components.",
    faith = "I serve all Arkati equally.  My shop carries symbols of all the major deities.",
    deeds = "Deeds of Lorminstra are among my most important stock.  Buy one before you go hunting.",
    lorminstra = "The Lady of the Dead is generous with second chances.  Purchase a deed before it is needed.",
    buy = "LIST to see my inventory.  BUY what your practice requires.",
    sell = "I accept donations of religious goods.  SELL them to me.",
    default = "Clentaran folds his hands.  'How may I be of service?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Clentaran arranges small holy symbols by deity, spacing them with ruler-like precision.",
    "Clentaran lights a stick of incense and places it before a small shrine in the corner.",
    "Clentaran murmurs a brief prayer over a newly arrived shipment of religious goods.",
    "Clentaran checks his inventory list with methodical care.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 60

return NPC
