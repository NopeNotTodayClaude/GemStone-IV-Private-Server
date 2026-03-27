-- NPC: Chaston Griffin
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Wehnimer's Landing area
local NPC = {}

NPC.template_id    = "chaston_griffin"
NPC.name           = "Chaston Griffin"
NPC.article        = ""
NPC.title          = "Blameless knight"
NPC.description    = "A fanatical Blameless knight whose righteousness has crossed into zealotry."
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
    default = "Chaston Griffin does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
