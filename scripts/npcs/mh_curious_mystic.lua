-- NPC: a curious mystic
-- Zone/Town: auto-placed  |  Room: 19359
local NPC = {}

NPC.template_id    = "mh_curious_mystic"
NPC.name           = "a curious mystic"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A robed figure studying arcane texts near the wizard guild entrance."
NPC.home_room_id   = 19359

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
    default = "a curious mystic doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
