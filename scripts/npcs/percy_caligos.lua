-- NPC: Percy Caligos
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Caligos Isle pawnshop
local NPC = {}

NPC.template_id    = "percy_caligos"
NPC.name           = "Percy Caligos"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A peculiar figure on Caligos whose function is unclear but whose presence is consistent."
NPC.home_room_id   = 26464  -- 0 = unplaced; assign room ID when deploying

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
    default = "Percy Caligos does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
