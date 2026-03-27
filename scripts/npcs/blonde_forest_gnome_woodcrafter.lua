-- NPC: Blonde forest gnome woodcrafter
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Cysaegir
local NPC = {}

NPC.template_id    = "blonde_forest_gnome_woodcrafter"
NPC.name           = "Blonde forest gnome woodcrafter"
NPC.article        = ""
NPC.title          = "woodcrafter"
NPC.description    = "A forest gnome craftsman whose tree-based creations blend function and artistry."
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
    default = "Blonde forest gnome woodcrafter does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
