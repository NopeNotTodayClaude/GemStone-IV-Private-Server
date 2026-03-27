-- NPC: Raven-haired aelotoi store clerk
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Cysaegir
local NPC = {}

NPC.template_id    = "raven_haired_aelotoi_store_clerk"
NPC.name           = "Raven-haired aelotoi store clerk"
NPC.article        = ""
NPC.title          = "store clerk"
NPC.description    = "An aelotoi clerk whose raven-dark hair and quiet efficiency make her a calming presence."
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
    default = "Raven-haired aelotoi store clerk does not respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
