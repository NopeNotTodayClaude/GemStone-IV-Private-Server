-- NPC: a forge clerk
-- Zone/Town: auto-placed  |  Room: 10394
local NPC = {}

NPC.template_id    = "tv_forge_clerk"
NPC.name           = "a forge clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A methodical elven scribe maintaining an exhaustive workshop inventory."
NPC.home_room_id   = 10394

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
    forge = "Ingots, charcoal, tongs, orders, receipts.  The romantic side of metalwork rarely reaches my desk.",
    supplies = "If the forge lacks something, the whole district hears about it by sunset.",
    inventory = "Inventory is merely memory written down before someone can forget profitably.",
    default = "The clerk looks up from a ledger.  'If you need supply information, ask directly.'",
}
NPC.ambient_emotes = {
    "The forge clerk licks a thumb and turns a page in a soot-smudged ledger.",
    "The forge clerk counts a stack of order slips twice, then ties them neatly together.",
    "The forge clerk checks a crate mark and makes a short note in the margin of a page.",
    "The forge clerk glances toward the workshop door at the sound of hammering.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
