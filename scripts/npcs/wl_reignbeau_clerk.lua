-- NPC: a dwarven dye clerk
-- Zone/Town: auto-placed  |  Room: 1253
local NPC = {}

NPC.template_id    = "wl_reignbeau_clerk"
NPC.name           = "a dwarven dye clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A grumbling dwarven clerk whose apron bears testament to every hue the shop carries."
NPC.home_room_id   = 1253

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
    default = "a dwarven dye clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
