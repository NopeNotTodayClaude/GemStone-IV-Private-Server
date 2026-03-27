-- NPC: Gearchel
-- Role: shopkeeper  |  Room: 12350
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "gearchel"
NPC.name           = "Gearchel"
NPC.article        = ""
NPC.title          = "the armorer"
NPC.description    = "A sturdy elven woman with silver-streaked auburn hair, wearing a leather apron over chainmail.  She has an air of military precision about her."
NPC.home_room_id   = 12350

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
NPC.shop_id        = 2

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks you over with a practiced eye."
NPC.dialogues = {
    armor = "From robes to full plate, I carry protection for every warrior.  Use LIST to browse.",
    shields = "A good shield has saved more lives than any sword.  I stock several types.  Learn to use one.",
    training = "Get Armor Use ranks before you buy anything heavy.  Plate on an untrained body will get you killed faster than nothing.",
    legion = "I maintain the Legion's armory contracts.  My civilian stock is the same quality.",
    buy = "LIST shows my inventory.  BUY what catches your eye.",
    sell = "I'll take armor off your hands for a fair price.  Just SELL it.",
    default = "Gearchel looks you over with a practiced eye.  'Need protection?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Gearchel adjusts the straps on a display suit of chain mail.",
    "Gearchel polishes a gleaming breastplate until it reflects the light.",
    "Gearchel tests the flex of a set of leather bracers.",
    "Gearchel runs her fingers along the links of a chain hauberk, checking for flaws.",
    "Gearchel marks something in a ledger with brisk efficiency.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
