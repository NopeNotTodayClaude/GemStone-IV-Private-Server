-- NPC: a dye merchant
-- Zone/Town: auto-placed  |  Room: 16847
local NPC = {}

NPC.template_id    = "zl_dye_mushroom_clerk"
NPC.name           = "a dye merchant"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A gnome dyer whose natural dyes come exclusively from underground fungus."
NPC.home_room_id   = 16847

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
    default = "a dye merchant doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
