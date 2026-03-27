-- NPC: a court clerk
-- Zone/Town: auto-placed  |  Room: 5907
local NPC = {}

NPC.template_id    = "tv_justice_clerk"
NPC.name           = "a court clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A precisely dressed elven official with a quill perpetually behind one ear."
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
    justice = "Petitions, fines, witness statements, summonses.  Civilization produces paperwork in astonishing volume.",
    court = "If you require the Hall of Justice, arrive prepared and concise.",
    records = "Properly filed records save everyone trouble except those hoping to avoid them.",
    gate = "I am here because official business occasionally insists on leaving the hall and standing in the wind.",
    default = "The clerk smooths a folded document.  'If you need a record checked, ask clearly.'",
}
NPC.ambient_emotes = {
    "The clerk checks a seal on a folded document and tucks it back into a case.",
    "The clerk makes a neat note on a narrow slate, then dusts the chalk from his fingers.",
    "The clerk studies the gate traffic with the expression of someone quietly matching faces to paperwork.",
    "The clerk adjusts the quill behind one ear without looking up.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
