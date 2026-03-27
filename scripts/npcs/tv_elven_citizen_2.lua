-- NPC: an elven merchant
-- Zone/Town: auto-placed  |  Room: 5907
local NPC = {}

NPC.template_id    = "tv_elven_citizen_2"
NPC.name           = "an elven merchant"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "An elven merchant carrying a slim leather satchel of papers."
NPC.home_room_id   = 5907

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
    trade = "South road caravans are slower this week.  Everyone blames the weather first and the wagoners second.",
    gate = "Victory Gate moves better than most city gates I've known.  Less shouting, more competence.",
    market = "If Phisk does not have it, he can usually tell you who does.",
    default = "The merchant offers a polite nod.  'Busy day at the gate.  Good for business.'",
}
NPC.ambient_emotes = {
    "The merchant loosens the strap of his satchel and checks a folded bill of sale.",
    "The merchant steps aside to let a pair of travelers pass, then resumes watching the road.",
    "The merchant counts quietly on his fingers, pauses, and starts over with a sigh.",
    "The merchant glances over the gate traffic with practiced commercial interest.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
