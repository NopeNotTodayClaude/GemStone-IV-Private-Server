-- NPC: Rockszie
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Zul Logoth
local NPC = {}

NPC.template_id    = "rockszie"
NPC.name           = "Rockszie"
NPC.article        = ""
NPC.title          = "gnome"
NPC.description    = "A gnome whose compact size and tunnel knowledge make her invaluable in specific difficult situations."
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
    default = "Rockszie does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
