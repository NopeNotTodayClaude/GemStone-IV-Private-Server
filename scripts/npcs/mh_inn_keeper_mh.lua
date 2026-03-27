-- NPC: an island innkeeper
-- Zone/Town: auto-placed  |  Room: 16411
local NPC = {}

NPC.template_id    = "mh_inn_keeper_mh"
NPC.name           = "an island innkeeper"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A cheerful human host whose inn is permeated with the scent of tropical flowers."
NPC.home_room_id   = 16411

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
    default = "an island innkeeper doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
