-- NPC: Daenvith
-- Zone/Town: auto-placed  |  Room: 3535
local NPC = {}

NPC.template_id    = "tv_daenvith"
NPC.name           = "a Hall sentry"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A disciplined elven sentry posted near the hall, with polished armor and an expression trained toward neutrality."
NPC.home_room_id   = 3535

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
    hall = "The hall remains open to those with business and patience in equal measure.",
    court = "This side of the court gets less shouting.  I am grateful for that.",
    duty = "Sentry work is simpler than politics and more honest than rumor.",
    default = "The sentry acknowledges you with a brief nod and resumes his watch.",
}
NPC.ambient_emotes = {
    "The sentry scans the approach to the hall with professional calm.",
    "The sentry adjusts the angle of a shield strap and returns to stillness.",
    "The sentry glances toward the court, then the hall doors, and settles again.",
    "The sentry rests both hands lightly on the butt of a grounded spear.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
