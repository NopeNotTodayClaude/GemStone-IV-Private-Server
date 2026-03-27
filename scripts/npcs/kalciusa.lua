-- NPC: Kalciusa
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Ta'Illistim
local NPC = {}

NPC.template_id    = "kalciusa"
NPC.name           = "Kalciusa"
NPC.article        = ""
NPC.title          = "elven administrator"
NPC.description    = "An elven woman whose position in the wizard guild spans both administrative and academic concerns."
NPC.home_room_id   = 18041

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = true
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    wizard = "The Wizard Guild refines magical discipline, item work, and precise control.  Talent is merely the entry fee.",
    join = "If you have reached the proper rank in your profession, I can enter your name in the guild rolls.",
    training = "A wizard's guild progress is earned through study, casting, and practical magical work.",
    scrolls = "Arcane symbols and scrollwork remain essential to any serious wizard.",
    charge = "Charged devices are useful only when their matrices are understood and respected.",
    default = "Kalciusa adjusts a stack of vellum forms.  'State your business clearly, if you please.'",
}
NPC.ambient_emotes = {
    "Kalciusa reviews a ledger of guild dues, making a neat correction in the margin.",
    "Kalciusa sets one crystal stylus aside and reaches for another without looking up.",
    "Kalciusa studies a shelf of scroll cases with the expression of someone cataloging possible disasters.",
}
NPC.ambient_chance = 0.025
NPC.emote_cooldown = 60
NPC.guild_id       = "wizard"

return NPC
