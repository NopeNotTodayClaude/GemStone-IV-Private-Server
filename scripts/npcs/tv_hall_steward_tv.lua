-- NPC: a hall steward
-- Zone/Town: auto-placed  |  Room: 3542
local NPC = {}

NPC.template_id    = "tv_hall_steward_tv"
NPC.name           = "a hall steward"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An impeccably attired elven steward overseeing the grand hall."
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
    hall = "The hall is running to schedule, which is how I prefer every day to begin.",
    court = "Victory Court is manageable so long as no one mistakes urgency for authority.",
    steward = "A steward's work is mostly preventing inconvenience before anyone notices it was possible.",
    default = "The steward inclines his head with polished courtesy.  'If you require direction, ask plainly.'",
}
NPC.ambient_emotes = {
    "The steward checks the drape of a banner with an exacting eye.",
    "The steward dispatches a runner with a few low words and a pointed finger.",
    "The steward surveys the square as though mentally rearranging it for efficiency.",
    "The steward smooths one immaculate sleeve and resumes his watch.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
