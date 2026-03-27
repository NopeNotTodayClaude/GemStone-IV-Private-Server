-- NPC: Morvule Thinevael
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Ta'Nalfein
local NPC = {}

NPC.template_id    = "morvule_thinevael"
NPC.name           = "Morvule Thinevael"
NPC.article        = ""
NPC.title          = "dark elf"
NPC.description    = "A dark elf of the Thinevael line whose loyalties between the houses remain unclear."
NPC.home_room_id   = 0  -- 0 = unplaced; assign room ID when deploying

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
    default = "Morvule Thinevael does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
