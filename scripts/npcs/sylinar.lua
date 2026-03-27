-- NPC: Sylinar
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Ta'Vaalor
local NPC = {}

NPC.template_id    = "sylinar"
NPC.name           = "Sylinar"
NPC.article        = ""
NPC.title          = "elven soldier"
NPC.description    = "An elven man whose patrol route through the city is both regular and well-informed."
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
    default = "Sylinar does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
