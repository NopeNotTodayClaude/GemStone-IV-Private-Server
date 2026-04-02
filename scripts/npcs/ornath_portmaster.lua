local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")
NPC.template_id = "ornath_portmaster"
NPC.name = "the portmaster"
NPC.article = ""
NPC.title = ""
NPC.description = "A sun-browned portmaster watches the Sleeping Drake harbor for the next outbound run."
NPC.home_room_id = 35254
NPC.can_combat = false NPC.can_shop = false NPC.can_wander = false NPC.can_emote = true NPC.can_chat = false NPC.can_loot = false NPC.is_guild = false NPC.is_quest = false NPC.is_house = false NPC.is_bot = false NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster flicks a glance up from the dock ledger.  'Where are you bound?'" }
NPC.ambient_emotes = { "The portmaster shades their eyes and studies the line of the outer harbor." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
TravelOfficeNPC.attach(NPC, "port_ornath")
return NPC
