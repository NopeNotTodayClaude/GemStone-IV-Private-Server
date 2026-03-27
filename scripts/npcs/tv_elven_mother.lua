-- NPC: an elven mother
-- Zone/Town: auto-placed  |  Room: 3542
local NPC = {}

NPC.template_id    = "tv_elven_mother"
NPC.name           = "an elven mother"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "An elven woman keeping a watchful eye on the child at her side."
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
    child = "If he asks the guards another dozen questions, one of them may eventually answer.",
    city = "A child learns a city first by the sounds of it and only later by the streets.",
    court = "Victory Court is safe enough by day if you keep an eye on quick feet and quicker hands.",
    default = "The mother offers a distracted smile.  'If you don't mind, I'm counting small disasters before they happen.'",
}
NPC.ambient_emotes = {
    "The mother smooths the child's hair back into place with practiced efficiency.",
    "The mother catches a small sleeve before its owner can wander too far from the square.",
    "The mother points out a passing patrol, and the child watches with solemn fascination.",
    "The mother adjusts a satchel on one shoulder and resumes her patient watch.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
