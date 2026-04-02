local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")
NPC.template_id = "marshtown_portmaster"
NPC.name = "the portmaster"
NPC.article = ""
NPC.title = ""
NPC.description = "A mud-spattered portmaster watches the pier with the resignation of someone used to brackish weather."
NPC.home_room_id = 11756
NPC.can_combat = false NPC.can_shop = false NPC.can_wander = false NPC.can_emote = true NPC.can_chat = false NPC.can_loot = false NPC.is_guild = false NPC.is_quest = false NPC.is_house = false NPC.is_bot = false NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster wipes a hand on a damp coat.  'Where to?'" }
NPC.ambient_emotes = { "The portmaster checks a tide mark etched into the dock pilings." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
TravelOfficeNPC.attach(NPC, "port_marshtown")
return NPC
