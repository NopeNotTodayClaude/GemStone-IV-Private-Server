-- NPC: Saphrie
-- Zone/Town: auto-placed  |  Room: 10396
local NPC = {}

NPC.template_id    = "tv_saphrie"
NPC.name           = "Saphrie"
NPC.article        = ""
NPC.title          = "master herbalist"
NPC.description    = "The proprietor of the herb shop, an elven woman of quiet expertise."
NPC.home_room_id   = 10396

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    herbs = "A good herb should be identified before it is admired.",
    tinctures = "Tinctures reward patience, clean glass, and exact ratios.  Mostly exact ratios.",
    forage = "Freshness matters.  So does not trampling half a field to gather one useful leaf.",
    default = "Saphrie studies you with calm attention.  'If you need herbs, say which sort.'",
}
NPC.ambient_emotes = {
    "Saphrie lifts a dried sprig to the light and inspects it with a critical eye.",
    "Saphrie rearranges a row of stoppered vials into a more exact alignment.",
    "Saphrie crushes a leaf between her fingers and considers the scent for a moment.",
    "Saphrie records a note in a narrow herbal ledger and sands the ink dry.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
