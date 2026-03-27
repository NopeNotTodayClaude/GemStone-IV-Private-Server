-- NPC: a cleric devotee
-- Zone/Town: auto-placed  |  Room: 18897
local NPC = {}

NPC.template_id    = "mh_cleric_devotee"
NPC.name           = "a cleric devotee"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A robed figure tending the vineyard shrine with meditative focus."
NPC.home_room_id   = 18897

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
    default = "a cleric devotee doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
