-- NPC: a scholarly pawnbroker
-- Zone/Town: auto-placed  |  Room: 644
local NPC = {}

NPC.template_id    = "tai_pawnbroker_tai"
NPC.name           = "a scholarly pawnbroker"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An elven merchant with an academic's appreciation for the objects that pass through his shop."
NPC.home_room_id   = 644

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
    default = "a scholarly pawnbroker doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
