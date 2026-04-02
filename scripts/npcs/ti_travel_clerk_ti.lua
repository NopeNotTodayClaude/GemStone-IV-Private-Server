-- NPC: a travel clerk
-- Zone/Town: auto-placed  |  Room: 1871
local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id    = "ti_travel_clerk_ti"
NPC.name           = "a travel clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A dwarven clerk managing transit schedules to and from the island."
NPC.home_room_id   = 1871

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
    travel = "The Glaesen Star does not wait on the indecisive.",
    airship = "If you need passage back to Wehnimer's Landing, say so plainly.",
    fares = "Airship passage is dearer than road travel, but far faster.",
    default = "The dwarven clerk taps a copper itinerary board.  'Wehnimer's or nowhere.  Which is it?'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

TravelOfficeNPC.attach(NPC, "kd_airship")

return NPC
