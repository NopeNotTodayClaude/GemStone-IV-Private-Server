-- NPC: a wyvern registrar
-- Zone/Town: auto-placed  |  Room: 10373
local NPC = {}

NPC.template_id    = "tv_wyvern_registrar"
NPC.name           = "a wyvern registrar"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An efficient elven official managing the Wyvern Battalion's administrative records."
NPC.home_room_id   = 10373

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
    wyvern = "Aerial service produces a remarkable quantity of forms for something so determinedly dramatic.",
    records = "A registrar's purpose is to make sure no one can later claim they were never told.",
    register = "If your paperwork is complete, I am helpful.  If it is not, I am educational.",
    default = "The registrar adjusts a stack of forms.  'Registration, records, or reassignment?'",
}
NPC.ambient_emotes = {
    "The registrar straightens a stack of forms until the edges align perfectly.",
    "The registrar checks a name against a roster and marks a tidy notation beside it.",
    "The registrar seals a document with quick, practiced precision.",
    "The registrar glances skyward at a distant wing-shadow, then returns to the ledger.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
