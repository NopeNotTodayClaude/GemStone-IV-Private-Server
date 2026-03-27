-- NPC: a dye merchant
-- Zone/Town: auto-placed  |  Room: 16175
local NPC = {}

NPC.template_id    = "rr_dye_merchant_rr"
NPC.name           = "a dye merchant"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A cheerful human woman running the bamboo cottage dye shop."
NPC.home_room_id   = 16175

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
