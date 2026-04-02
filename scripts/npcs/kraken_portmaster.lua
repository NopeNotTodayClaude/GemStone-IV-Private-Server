local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")
NPC.template_id = "kraken_portmaster"
NPC.name = "the portmaster"
NPC.article = ""
NPC.title = ""
NPC.description = "A harbor official in weather-darkened leathers watches the first pier with cold efficiency."
NPC.home_room_id = 29033
NPC.can_combat = false NPC.can_shop = false NPC.can_wander = false NPC.can_emote = true NPC.can_chat = false NPC.can_loot = false NPC.is_guild = false NPC.is_quest = false NPC.is_house = false NPC.is_bot = false NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster folds a manifest shut.  'Name the pier you want.'" }
NPC.ambient_emotes = { "The portmaster checks the wind and scratches out a note beside a departure time." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
TravelOfficeNPC.attach(NPC, "port_kraken")
return NPC
