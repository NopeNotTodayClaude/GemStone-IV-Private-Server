-- NPC: a dwarven innkeeper
-- Zone/Town: auto-placed  |  Room: 1842
local NPC = {}

NPC.template_id    = "ti_inn_keeper_ti"
NPC.name           = "a dwarven innkeeper"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A stout dwarven host whose inn has been serving travelers for three generations."
NPC.home_room_id   = 1842

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
    default = "a dwarven innkeeper doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
