-- NPC: Drevith
-- Role: shopkeeper  |  Room: 10368
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "rations_clerk"
NPC.name           = "Drevith"
NPC.article        = ""
NPC.title          = "the provisioner"
NPC.description    = "A lean elven man with the efficient manner of someone who has supplied armies.  Every item in his shop is exactly where it should be."
NPC.home_room_id   = 10368

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
NPC.shop_id        = 14

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "nods with the brisk efficiency of someone always busy."
NPC.dialogues = {
    rations = "I stock everything a soldier or traveler needs for the road.  Durable, nourishing, ready to go.",
    food = "Field rations are my specialty.  Also fresh provisions if you prefer something that hasn't been dried.",
    travel = "Heading to Neartofar?  The road south from the Annatto Gate.  Stock up before you leave.",
    legion = "I supply the Legion field rations.  Same stock available to civilians.",
    buy = "LIST to see what I've got.  BUY what you need.",
    default = "Drevith looks up.  'Provisioning for a journey?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Drevith checks the seal on a bundle of travel rations and sets it aside.",
    "Drevith counts a row of waterskins with quick, practiced efficiency.",
    "Drevith marks something off a supply list and moves to the next shelf.",
    "Drevith restacks a row of bread loaves, keeping the freshest ones in front.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
