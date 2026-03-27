-- NPC: Peg-legged halfling bartender
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: River's Rest
local NPC = {}

NPC.template_id    = "peg_legged_halfling_bartender"
NPC.name           = "Peg-legged halfling bartender"
NPC.article        = ""
NPC.title          = "bartender"
NPC.description    = "A halfling bartender whose prosthetic leg is both a conversation piece and a weapon of last resort."
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
    default = "Peg-legged halfling bartender does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
