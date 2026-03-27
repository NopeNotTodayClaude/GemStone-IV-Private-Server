-- NPC: an elven citizen
-- Zone/Town: auto-placed  |  Room: 3542
local NPC = {}

NPC.template_id    = "tv_elven_citizen_1"
NPC.name           = "an elven citizen"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A well-dressed elven citizen going about the business of daily life."
NPC.home_room_id   = 3542

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
    city = "Ta'Vaalor runs well because too many people would be embarrassed to let it run poorly.",
    court = "Victory Court is useful if you want to hear three errands, two rumors, and one lecture before lunch.",
    legion = "The Legion keeps order.  The rest of us keep schedules.",
    default = "The citizen inclines his head.  'Fine weather for business, if not for leisure.'",
}
NPC.ambient_emotes = {
    "The citizen pauses at the fountain to glance over a folded list of errands.",
    "The citizen trades a brief greeting with a passing guard and continues on.",
    "The citizen adjusts a cuff with absent precision and surveys the square.",
    "The citizen glances toward the Hall of Justice, then changes course as if remembering something urgent.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 75

return NPC
