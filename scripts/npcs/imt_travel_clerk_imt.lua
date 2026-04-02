-- NPC: a travel clerk
-- Zone/Town: auto-placed  |  Room: 3411
local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id    = "imt_travel_clerk_imt"
NPC.name           = "a travel clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A brisk halfling coordinating travel arrangements with surprising organizational skill."
NPC.home_room_id   = 3411

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
    travel = "The snow doesn't slow the roads half so much as indecision does.",
    destinations = "If you want out of Icemule, say where.",
    fares = "Travel guide fees are cheaper than getting lost in a drift.",
    default = "The halfling clerk peers over a stack of route cards.  'Pick your town.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

TravelOfficeNPC.attach(NPC, "imt_travel")

return NPC
