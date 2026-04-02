local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")
NPC.template_id = "rr_portmaster"
NPC.name = "the portmaster"
NPC.article = ""
NPC.title = ""
NPC.description = "A river portmaster keeps one eye on the underbridge docks and one on the posted fares."
NPC.home_room_id = 10838
NPC.can_combat = false NPC.can_shop = false NPC.can_wander = false NPC.can_emote = true NPC.can_chat = false NPC.can_loot = false NPC.is_guild = false NPC.is_quest = false NPC.is_house = false NPC.is_bot = false NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster taps the fare board.  'Where are you sailing?'" }
NPC.ambient_emotes = { "The portmaster squints downriver and mutters a quick estimate of the tide." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
TravelOfficeNPC.attach(NPC, "port_rr")
return NPC
