-- NPC: Urgaen
-- Zone/Town: auto-placed  |  Room: 4683
local NPC = {}

NPC.template_id    = "cys_pawnbroker_urgaen"
NPC.name           = "Urgaen"
NPC.article        = ""
NPC.title          = "pawnbroker"
NPC.description    = "An aelotoi merchant with an eye for undervalued goods."
NPC.home_room_id   = 4683

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
    default = "Urgaen doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
