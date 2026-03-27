-- NPC: Yrmythia Gael
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Ta'Illistim court
local NPC = {}

NPC.template_id    = "yrmythia_gael"
NPC.name           = "Yrmythia Gael"
NPC.article        = ""
NPC.title          = "Illistim noble"
NPC.description    = "An elven noblewoman of the Gael Illistim line whose court position involves managing cultural matters of sensitivity."
NPC.home_room_id   = 11  -- 0 = unplaced; assign room ID when deploying

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
    default = "Yrmythia Gael does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
