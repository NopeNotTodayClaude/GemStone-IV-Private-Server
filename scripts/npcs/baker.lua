-- NPC: Sweethen
-- Role: shopkeeper  |  Room: 12349
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "baker"
NPC.name           = "Sweethen"
NPC.article        = ""
NPC.title          = "the baker"
NPC.description    = "A round-cheeked elven woman perpetually dusted with flour, with a warm smile and the inviting smell of fresh bread about her."
NPC.home_room_id   = 12349

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
NPC.shop_id        = 17

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks up from kneading dough.  'Something sweet for the road?'"
NPC.dialogues = {
    bread = "Fresh from the oven every morning.  Honey rolls are today's special.",
    pastry = "I bake everything from field rations to elaborate pastries for court functions.",
    rations = "I make field rations for the Legion.  Durable, nourishing, and - I insist - not terrible.",
    default = "Sweethen smiles broadly.  'Something smells good, doesn't it?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Sweethen slides a tray of golden rolls out of the oven.",
    "Sweethen kneads a mound of dough with practiced, rhythmic motions.",
    "Sweethen pipes delicate icing onto a row of small cakes.",
    "Sweethen hums to herself while measuring flour.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
