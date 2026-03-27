-- NPC: Omlor
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Zul Logoth
local NPC = {}

NPC.template_id    = "omlor"
NPC.name           = "Omlor"
NPC.article        = ""
NPC.title          = "dwarven structural engineer"
NPC.description    = "A dwarven man whose knowledge of Zul Logoth's structural weaknesses is the foundation of its maintenance."
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
    default = "Omlor does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
