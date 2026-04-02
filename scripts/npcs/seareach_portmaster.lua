local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")
NPC.template_id = "seareach_portmaster"
NPC.name = "the portmaster"
NPC.article = ""
NPC.title = ""
NPC.description = "A lean portmaster keeps a careful eye on Pier 5 and the cargo moving through it."
NPC.home_room_id = 32928
NPC.can_combat = false NPC.can_shop = false NPC.can_wander = false NPC.can_emote = true NPC.can_chat = false NPC.can_loot = false NPC.is_guild = false NPC.is_quest = false NPC.is_house = false NPC.is_bot = false NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster rolls a manifest into a tube.  'Destination?'" }
NPC.ambient_emotes = { "The portmaster glances between the pier and a slate of departure marks." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
TravelOfficeNPC.attach(NPC, "port_seareach")
return NPC
