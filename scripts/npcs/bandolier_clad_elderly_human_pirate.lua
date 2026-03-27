-- NPC: Bandolier-clad elderly human pirate
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Kraken's Fall
local NPC = {}

NPC.template_id    = "bandolier_clad_elderly_human_pirate"
NPC.name           = "Bandolier-clad elderly human pirate"
NPC.article        = ""
NPC.title          = "pirate"
NPC.description    = "An elderly mariner whose impressive collection of weaponry suggests a rich career."
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
    default = "Bandolier-clad elderly human pirate does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
