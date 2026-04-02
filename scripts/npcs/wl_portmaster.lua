local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")
NPC.template_id = "wl_portmaster"
NPC.name = "the portmaster"
NPC.article = ""
NPC.title = ""
NPC.description = "A dockside official with a ledger tucked beneath one arm watches the harbor traffic with practiced impatience."
NPC.home_room_id = 250
NPC.can_combat = false NPC.can_shop = false NPC.can_wander = false NPC.can_emote = true NPC.can_chat = false NPC.can_loot = false NPC.is_guild = false NPC.is_quest = false NPC.is_house = false NPC.is_bot = false NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster jerks a thumb toward the moorings.  'Name the harbor.'" }
NPC.ambient_emotes = { "The portmaster glances over a damp page of fares and departures." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
TravelOfficeNPC.attach(NPC, "port_wl")
return NPC
