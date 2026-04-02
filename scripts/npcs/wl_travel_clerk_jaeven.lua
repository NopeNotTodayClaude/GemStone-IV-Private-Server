-- NPC: Post clerk Jaeven
-- Zone/Town: auto-placed  |  Room: 8632
local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id    = "wl_travel_clerk_jaeven"
NPC.name           = "Post clerk Jaeven"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A bespectacled gnome buried under a mountain of delivery manifests."
NPC.home_room_id   = 8632

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
    travel = "If you need a road guide, name your town cleanly.",
    destinations = "I can route you through the other guide offices if you qualify.",
    fares = "Guide travel is cheap.  The wasted time from wandering is not.",
    default = "Post clerk Jaeven squints over a stack of manifests.  'Name the town and keep the line moving.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

TravelOfficeNPC.attach(NPC, "wl_travel")

return NPC
