local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "nielira_portmaster"
NPC.name = "the portmaster"
NPC.article = "the"
NPC.title = ""
NPC.description = "A weathered portmaster stands over the Nielira fare board with the patience of someone used to explaining the tides twice."
NPC.home_room_id = 33856
NPC.can_combat = false
NPC.can_shop = false
NPC.can_wander = false
NPC.can_emote = true
NPC.can_chat = false
NPC.can_loot = false
NPC.is_guild = false
NPC.is_quest = false
NPC.is_house = false
NPC.is_bot = false
NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster studies the harbor.  'Name the dock you need.'" }
NPC.ambient_emotes = { "The portmaster glances over the harbor board and scratches a correction into the margin." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

TravelOfficeNPC.attach(NPC, "port_nielira")

return NPC
